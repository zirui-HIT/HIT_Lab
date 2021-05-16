/**
 * @author Zhaonian Zou <znzou@hit.edu.cn>,
 * School of Computer Science and Technology,
 * Harbin Institute of Technology, China
 */

#include "executor.h"

#include "exceptions/buffer_exceeded_exception.h"
#include <cmath>
#include <ctime>
#include <functional>
#include <iostream>
#include <cstring>
#include <utility>

#include "file_iterator.h"
#include "page_iterator.h"
#include "storage.h"

vector<string> analyze(string record, badgerdb::TableSchema schema);

using namespace std;

namespace badgerdb
{

  void TableScanner::print() const
  {
    badgerdb::File file = badgerdb::File::open(tableFile.filename());
    for (badgerdb::FileIterator iter = file.begin(); iter != file.end(); ++iter)
    {
      badgerdb::Page page = *iter;
      badgerdb::Page *buffered_page;
      bufMgr->readPage(&file, page.page_number(), buffered_page);

      for (badgerdb::PageIterator page_iter = buffered_page->begin();
           page_iter != buffered_page->end(); ++page_iter)
      {
        string key = *page_iter;
        string print_key = "(";
        int current_index = 0;
        for (int i = 0; i < tableSchema.getAttrCount(); ++i)
        {
          switch (tableSchema.getAttrType(i))
          {
          case INT:
          {
            int true_value = 0;
            for (int j = 0; j < 4; ++j)
            {
              if (std::string(key, current_index + j, 1)[0] == '\0')
              {
                continue; // \0 is actually representing 0
              }
              true_value +=
                  (std::string(key, current_index + j, 1))[0] * pow(128, 3 - j);
            }
            print_key += to_string(true_value);
            current_index += 4;
            break;
          }
          case CHAR:
          {
            int max_len = tableSchema.getAttrMaxSize(i);
            print_key += std::string(key, current_index, max_len);
            current_index += max_len;
            current_index +=
                (4 - (max_len % 4)) % 4; // align to the multiple of 4
            break;
          }
          case VARCHAR:
          {
            int actual_len = key[current_index];
            current_index++;
            print_key += std::string(key, current_index, actual_len);
            current_index += actual_len;
            current_index +=
                (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
            break;
          }
          }
          print_key += ",";
        }
        print_key[print_key.size() - 1] = ')'; // change the last ',' to ')'
        cout << print_key << endl;
      }
      bufMgr->unPinPage(&file, page.page_number(), false);
    }
    bufMgr->flushFile(&file);
  }

  JoinOperator::JoinOperator(const File &leftTableFile,
                             const File &rightTableFile,
                             const TableSchema &leftTableSchema,
                             const TableSchema &rightTableSchema,
                             const Catalog *catalog,
                             BufMgr *bufMgr)
      : leftTableFile(leftTableFile),
        rightTableFile(rightTableFile),
        leftTableSchema(leftTableSchema),
        rightTableSchema(rightTableSchema),
        resultTableSchema(
            createResultTableSchema(leftTableSchema, rightTableSchema)),
        catalog(catalog),
        bufMgr(bufMgr),
        isComplete(false)
  {
    // nothing
  }

  TableSchema JoinOperator::createResultTableSchema(
      const TableSchema &leftTableSchema,
      const TableSchema &rightTableSchema)
  {
    vector<Attribute> attrs;

    // first add all the left table attrs to the result table
    for (int k = 0; k < leftTableSchema.getAttrCount(); ++k)
    {
      Attribute new_attr = Attribute(
          leftTableSchema.getAttrName(k), leftTableSchema.getAttrType(k),
          leftTableSchema.getAttrMaxSize(k), leftTableSchema.isAttrNotNull(k),
          leftTableSchema.isAttrUnique(k));
      attrs.push_back(new_attr);
    }

    // test every right table attrs, if it doesn't have the same attr(name and
    // type) in the left table, then add it to the result table
    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      bool has_same = false;
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          has_same = true;
        }
      }
      if (!has_same)
      {
        Attribute new_attr = Attribute(
            rightTableSchema.getAttrName(i), rightTableSchema.getAttrType(i),
            rightTableSchema.getAttrMaxSize(i), rightTableSchema.isAttrNotNull(i),
            rightTableSchema.isAttrUnique(i));
        attrs.push_back(new_attr);
      }
    }
    return TableSchema("TEMP_TABLE", attrs, true);
  }

  void JoinOperator::printRunningStats() const
  {
    cout << "# Result Tuples: " << numResultTuples << endl;
    cout << "# Used Buffer Pages: " << numUsedBufPages << endl;
    cout << "# I/Os: " << numIOs << endl;
  }

  vector<Attribute> JoinOperator::getCommonAttributes(
      const TableSchema &leftTableSchema,
      const TableSchema &rightTableSchema) const
  {
    vector<Attribute> common_attrs;
    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          Attribute new_attr = Attribute(rightTableSchema.getAttrName(i),
                                         rightTableSchema.getAttrType(i),
                                         rightTableSchema.getAttrMaxSize(i),
                                         rightTableSchema.isAttrNotNull(i),
                                         rightTableSchema.isAttrUnique(i));
          common_attrs.push_back(new_attr);
        }
      }
    }
    return common_attrs;
  }

  string JoinOperator::joinTuples(string leftTuple,
                                  string rightTuple,
                                  const TableSchema &leftTableSchema,
                                  const TableSchema &rightTableSchema) const
  {
    int cur_right_index = 0; // current substring index in the right table key
    string result_tuple = leftTuple;

    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      bool has_same = false;
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          has_same = true;
        }
      }
      // if the key is only owned by right table, add it to the result tuple
      switch (rightTableSchema.getAttrType(i))
      {
      case INT:
      {
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, 4);
        }
        cur_right_index += 4;
        break;
      }
      case CHAR:
      {
        int max_len = rightTableSchema.getAttrMaxSize(i);
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, max_len);
        }
        cur_right_index += max_len;
        unsigned align_ = (4 - (max_len % 4)) % 4; // align to the multiple of
                                                   // 4
        for (int k = 0; k < align_; ++k)
        {
          result_tuple += "0";
          cur_right_index++;
        }
        break;
      }
      case VARCHAR:
      {
        int actual_len = rightTuple[cur_right_index];
        result_tuple += std::string(rightTuple, cur_right_index, 1);
        cur_right_index++;
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, actual_len);
        }
        cur_right_index += actual_len;
        unsigned align_ =
            (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
        for (int k = 0; k < align_; ++k)
        {
          result_tuple += "0";
          cur_right_index++;
        }
        break;
      }
      }
    }
    return result_tuple;
  }

  bool OnePassJoinOperator::execute(int numAvailableBufPages, File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 0;
    numIOs = 0;

    // TODO: Implement the one-pass join algorithm (NOT required in project 3)

    isComplete = true;
    return true;
  }

  bool NestedLoopJoinOperator::execute(int numAvailableBufPages,
                                       File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 0;
    numIOs = 0;

    TableId leftTableId = catalog->getTableId("r");
    TableId rightTableId = catalog->getTableId("s");
    badgerdb::File left = File::open(catalog->getTableFilename(leftTableId));
    badgerdb::File right = File::open(catalog->getTableFilename(rightTableId));

    int leftForeignKeyId = -1;
    int rightForeignKeyId = -1;
    for (int i = 0; i < leftTableSchema.getAttrCount(); i++)
    {
      for (int j = 0; j < rightTableSchema.getAttrCount(); j++)
      {
        if ((leftTableSchema.getAttrName(i) == rightTableSchema.getAttrName(j)) && (leftTableSchema.getAttrType(i) == rightTableSchema.getAttrType(j)))
        {
          leftForeignKeyId = i;
          rightForeignKeyId = j;
          break;
        }
      }
      if (rightForeignKeyId != -1)
      {
        break;
      }
    }

    vector<vector<string>> block;
    const int BLOCK_SIZE = 100;

    for (badgerdb::FileIterator leftPage = left.begin(); leftPage != left.end(); leftPage++)
    {
      badgerdb::Page *bufferedLeftPage;
      bufMgr->readPage(&left, (*leftPage).page_number(), bufferedLeftPage);
      numIOs += 1;

      for (badgerdb::FileIterator rightPage = right.begin(); rightPage != right.end(); rightPage++)
      {
        badgerdb::Page *bufferedRightPage;
        bufMgr->readPage(&right, (*rightPage).page_number(), bufferedRightPage);
        numIOs += 1;

        for (badgerdb::PageIterator leftRecord = bufferedLeftPage->begin(); leftRecord != bufferedLeftPage->end(); leftRecord++)
        {
          vector<string> leftInfo = analyze(*leftRecord, leftTableSchema);
          numUsedBufPages += 1;
          block.push_back(leftInfo);
          if (block.size() < BLOCK_SIZE)
          {
            continue;
          }

          for (badgerdb::PageIterator rightRecord = bufferedRightPage->begin(); rightRecord != bufferedRightPage->end(); rightRecord++)
          {
            numUsedBufPages += 1;
            for (int i = 0; i < block.size(); i++)
            {
              vector<string> leftInfo = block[i];
              vector<string> rightInfo = analyze(*rightRecord, rightTableSchema);

              if (leftInfo[leftForeignKeyId] == rightInfo[rightForeignKeyId])
              {
                string current_line = "INSERT INTO TEMP_TABLE VALUES (" + leftInfo[0];
                for (int i = 1; i < leftTableSchema.getAttrCount(); i++)
                {
                  current_line = current_line + ", " + leftInfo[i];
                }
                for (int i = 0; i < rightTableSchema.getAttrCount(); i++)
                {
                  bool flag = true;
                  for (int j = 0; j < leftTableSchema.getAttrCount(); j++)
                  {
                    if (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i) && leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i))
                    {
                      flag = false;
                      break;
                    }
                  }
                  if (flag)
                  {
                    current_line = current_line + ", " + rightInfo[i];
                  }
                }
                current_line = current_line + ");";

                string tuple = HeapFileManager::createTupleFromSQLStatement(current_line, catalog);
                numResultTuples += 1;
                HeapFileManager::insertTuple(tuple, resultFile, bufMgr);
              }
            }
          }

          block.clear();
        }

        // process record left in block
        if (block.size() > 0)
        {
          for (badgerdb::PageIterator rightRecord = bufferedRightPage->begin(); rightRecord != bufferedRightPage->end(); rightRecord++)
          {
            numUsedBufPages += 1;
            for (int i = 0; i < block.size(); i++)
            {
              vector<string> leftInfo = block[i];
              vector<string> rightInfo = analyze(*rightRecord, rightTableSchema);

              if (leftInfo[leftForeignKeyId] == rightInfo[rightForeignKeyId])
              {
                string current_line = "INSERT INTO TEMP_TABLE VALUES (" + leftInfo[0];
                for (int i = 1; i < leftTableSchema.getAttrCount(); i++)
                {
                  current_line = current_line + ", " + leftInfo[i];
                }
                for (int i = 0; i < rightTableSchema.getAttrCount(); i++)
                {
                  bool flag = true;
                  for (int j = 0; j < leftTableSchema.getAttrCount(); j++)
                  {
                    if (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i) && leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i))
                    {
                      flag = false;
                      break;
                    }
                  }
                  if (flag)
                  {
                    current_line = current_line + ", " + rightInfo[i];
                  }
                }
                current_line = current_line + ");";

                string tuple = HeapFileManager::createTupleFromSQLStatement(current_line, catalog);
                numResultTuples += 1;
                HeapFileManager::insertTuple(tuple, resultFile, bufMgr);
              }
            }
          }
        }
      }
    }

    isComplete = true;
    return true;
  }

  BucketId GraceHashJoinOperator::hash(const string &key) const
  {
    std::hash<string> strHash;
    return strHash(key) % numBuckets;
  }

  bool GraceHashJoinOperator::execute(int numAvailableBufPages,
                                      File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 0;
    numIOs = 0;

    // TODO: Implement the Grace hash join algorithm (NOT required in project 3)

    isComplete = true;
    return true;
  }
} // namespace badgerdb

vector<string> analyze(string record, badgerdb::TableSchema schema)
{
  vector<string> ret;
  int prev = 0;
  for (int i = 0; i < schema.getAttrCount(); i++)
  {
    int current_length = schema.getAttrMaxSize(i);
    int current_type = schema.getAttrType(i);
    int length = 0;

    switch (current_type)
    {
    case badgerdb::INT:
    {
      length = current_length;
      int current = 0;
      for (int i = 0; i < length; i++)
      {
        current += (int)record[i + prev] * pow(128, 3 - i);
      }
      ret.push_back(to_string(current));
      break;
    }
    case badgerdb::CHAR:
    {
      length = current_length;
      ret.push_back(record.substr(prev, length));
      break;
    }
    case badgerdb::VARCHAR:
    {
      int size = record[prev];
      prev += 1;
      length = size + (4 - ((size + 1) % 4)) % 4;
      ret.push_back(record.substr(prev, length));
      break;
    }
    }

    prev += length;
  }

  return ret;
}