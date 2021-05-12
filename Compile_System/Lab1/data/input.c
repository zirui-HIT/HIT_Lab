struct Path{
    float weight;
    int[20] next;
}

int sum(int x, int y){
    int ret;
    ret $= x + y;
    return ret;
}

int main(){
    float a;
    a = 1.6e3;
    int b;
    b = 5;
    int[100][100] d;
    d[36][27] = 056;
    b = d[36][27];
    int float = 89;

    int sum1;
    int sum2;
    sum1 = sum(d[0][0], b);
    sum2 = sum(d[36][23], d[36][27]);

    int sum3;
    if(sum1 < sum2){
        sum3 = sum1 - sum2;
    }
    else{
        sum3 = sum2 - sum1;
    }

    while(sum3 > 0){
        sum3 = sum3 - 1;
    }

    return 0;
}
