module full_adder_usingdecoder(input [2:0]in,output sum,carry);
wire [7:0]m;
decoder3_8 A1 (
        .in(in),
        .out(m) 
    );
assign sum=m[1]|m[2]|m[4]|m[7];
assign carry=m[3]|m[5]|m[6]|m[7];
endmodule