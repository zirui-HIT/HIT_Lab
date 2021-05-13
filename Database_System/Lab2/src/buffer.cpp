/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

#include <memory>
#include <iostream>
#include "buffer.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"
#include "exceptions/types.h"

namespace badgerdb
{

	BufMgr::BufMgr(std::uint32_t bufs)
		: numBufs(bufs)
	{
		bufDescTable = new BufDesc[bufs];

		for (FrameId i = 0; i < bufs; i++)
		{
			bufDescTable[i].frameNo = i;
			bufDescTable[i].valid = false;
		}

		bufPool = new Page[bufs];

		int htsize = ((((int)(bufs * 1.2)) * 2) / 2) + 1;
		hashTable = new BufHashTbl(htsize); // allocate the buffer hash table

		clockHand = bufs - 1;
	}

	BufMgr::~BufMgr()
	{
		delete[] bufDescTable;
		delete[] bufPool;
		delete hashTable;
	}

	void BufMgr::advanceClock()
	{
		// increase clock hand
		clockHand = (clockHand + 1) % numBufs;
	}

	void BufMgr::allocBuf(FrameId &frame)
	{
		FrameId lastClockHand = clockHand;
		unsigned int pinnedCount = 0;
		while (true)
		{
			advanceClock();

			// find available position
			if (!bufDescTable[clockHand].valid)
			{
				frame = clockHand;
				bufDescTable[clockHand].valid = true;
				return;
			}
			if (bufDescTable[clockHand].pinCnt > 0){
				pinnedCount += 1;
				if(pinnedCount == numBufs){
					throw BufferExceededException();
				}
				continue;
			}
			if (bufDescTable[clockHand].refbit)
			{
				bufDescTable[clockHand].refbit = false;
				continue;
			}

			// allocate position
			if (bufDescTable[clockHand].dirty)
			{
				bufDescTable[clockHand].file->writePage(bufPool[clockHand]);
				bufDescTable[clockHand].dirty = false;
			}
			frame = clockHand;
			try
			{
				hashTable->remove(bufDescTable[clockHand].file, bufDescTable[clockHand].pageNo);
			}
			catch (HashNotFoundException e)
			{
				// handle hash not found exception
				return;
			}

			if (lastClockHand == clockHand)
				throw BufferExceededException();
			break;
		}
	}

	void BufMgr::readPage(File *file, const PageId pageNo, Page *&page)
	{
		FrameId frame;
		try
		{
			hashTable->lookup(file, pageNo, frame);

			bufDescTable[frame].refbit = true;
			bufDescTable[frame].pinCnt++;
			page = &bufPool[frame];
		}
		catch (HashNotFoundException e)
		{
			allocBuf(frame);
			bufPool[frame] = file->readPage(pageNo);
			hashTable->insert(file, pageNo, frame);
			bufDescTable[frame].Set(file, pageNo);
			page = &bufPool[frame];
		}
	}

	void BufMgr::unPinPage(File *file, const PageId pageNo, const bool dirty)
	{
		FrameId frame;
		try
		{
			hashTable->lookup(file, pageNo, frame);
		}
		catch (HashNotFoundException e)
		{
			// handle hash not found exception
			return;
		}

		if (bufDescTable[frame].pinCnt > 0)
		{
			bufDescTable[frame].pinCnt--;
			if (dirty)
			{
				bufDescTable[frame].dirty = true;
			}
		}
		else
		{
			throw PageNotPinnedException(bufDescTable[frame].file->filename(), bufDescTable[frame].pageNo, frame);
		}
	}

	void BufMgr::flushFile(const File *file)
	{
		for(FrameId i = 0; i < numBufs; i++){
			if(bufDescTable[i].file == file){
				BufDesc currentDesc = bufDescTable[i];
				if(!currentDesc.valid){
					// empty desc
					throw BadBufferException(i, currentDesc.dirty, currentDesc.valid, currentDesc.refbit);
				}
				if(currentDesc.pinCnt > 0){
					// desc is still used
					throw PagePinnedException(file->filename(), currentDesc.pageNo, i);
				}
				if(currentDesc.dirty){
					// to be writen back
					currentDesc.file->writePage(bufPool[i]);
					currentDesc.dirty = false;
				}

				hashTable->remove(file, currentDesc.pageNo);
				currentDesc.Clear();
			}
		}
	}

	void BufMgr::allocPage(File *file, PageId &pageNo, Page *&page)
	{
		FrameId frame;
		Page p = file->allocatePage();
		allocBuf(frame);
		bufPool[frame] = p;
		pageNo = p.page_number();
		hashTable->insert(file, pageNo, frame);
		bufDescTable[frame].Set(file, pageNo);
		page = &bufPool[frame];
	}

	void BufMgr::disposePage(File *file, const PageId PageNo)
	{
	}

	void BufMgr::printSelf(void)
	{
		BufDesc *tmpbuf;
		int validFrames = 0;

		for (std::uint32_t i = 0; i < numBufs; i++)
		{
			tmpbuf = &(bufDescTable[i]);
			std::cout << "FrameNo:" << i << " ";
			tmpbuf->Print();

			if (tmpbuf->valid == true)
				validFrames++;
		}

		std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
	}

}
