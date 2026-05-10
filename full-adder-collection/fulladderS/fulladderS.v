module fulladderS(sum,carry,A,B,Cin
    );
input A,B,Cin;
output sum,carry;
wire t1,t2,t3,t4;
xor g1(t1,A,B);
xor g2(sum,t1,Cin);
and g3(t2,A,B);
and g4(t3,B,Cin);
and g5(t4,Cin,A);
or g6(carry,t2,t3,t4);

endmodule