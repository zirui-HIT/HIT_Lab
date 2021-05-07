int sum(float a, int b){
    float ret;
    ret $= a + b;
    return ret;
}

int main(){
    float a;
    a = 1.6e3;
    int b;
    b = 00xA5;
    float * c;
    c = 10.0;
    int[100][100] d;
    d[36][27] = 056;
    b = d[36][27];
    int float = 89;

    int sum1;
    int sum2;
    sum1 = sum(a, b);
    sum2 = sum(c, d);

    int sum3;
    if(sum1 < sum2){
        sum3 = sum1 - sum2;
    }
    else{
        sum3 = sum2 - sum1;
    }

    while(sum3 > 0){
        printf(sum3);
        sum3 = sum3 - 1;
    }
}
