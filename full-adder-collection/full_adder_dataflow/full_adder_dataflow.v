module full_adder_dataflow(s,c_out,a, b, c_in);

output s, c_out;
input a,b,c_in;
    
assign    s = a ^ b ^ c_in;
assign    c_out = (a & b) | (b & c_in) | (a & c_in);
endmodule