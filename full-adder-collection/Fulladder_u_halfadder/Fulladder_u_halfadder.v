module Fulladder_u_halfadder(a,b,cin,sum,carry);
input a,b,cin;
output sum,carry;
wire w1,w2,w3;
xor X1(w1,a,b);
and A1(w2,a,b);
xor X2(sum,w1,cin);
and A2(w3,w1,cin);
or O1(carry,w3,w2);
endmodule