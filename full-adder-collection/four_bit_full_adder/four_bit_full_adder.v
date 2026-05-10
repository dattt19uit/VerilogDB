module four_bit_full_adder(input [3:0]A,B,input carry_in,output [3:0]sum,output carry);

wire c1,c2,c3;

full_adder fa1(.a(A[0]),.b(B[0]),.cin(carry_in),.cout(c1),.sout(sum[0]));

full_adder fa2(.a(A[1]),.b(B[1]),.cin(c1),.cout(c2),.sout(sum[1]));

full_adder fa3(.a(A[2]),.b(B[2]),.cin(c2),.cout(c3),.sout(sum[2]));

full_adder fa4(.a(A[3]),.b(B[3]),.cin(c3),.cout(carry),.sout(sum[3]));

endmodule