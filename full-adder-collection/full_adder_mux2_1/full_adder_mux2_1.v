module full_adder_mux2_1(a,b,c_in,sum,carry_out);
input a,b,c_in;
output sum,carry_out;
wire w1,w2,w3,w4,w5;

//generating complement of "b"
mux_2_1 M1(.in_0(1'b1),.in_1(1'b0),.sel(b),.out(w1));

//generating complement of "c"
mux_2_1 M2(.in_0(1'b1),.in_1(1'b0),.sel(c_in),.out(w3));

//a xor b
mux_2_1 M3(.in_0(b),.in_1(w1),.sel(a),.out(w2));

//a xor b xor c
mux_2_1 M4(.in_0(c_in),.in_1(w3),.sel(w2),.out(sum));

//(a xor b)c_in
mux_2_1 M5(.in_0(1'b0),.in_1(c_in),.sel(w2),.out(w4));

//ab
mux_2_1 M6(.in_0(1'b0),.in_1(b),.sel(a),.out(w5));

//carry output
mux_2_1 M7(.in_0(w4),.in_1(1'b1),.sel(w5),.out(carry_out));

endmodule