module Full_Adder_1(
    input wire a,
    input wire b,
    input wire c_in,
    output wire c_out,
    output wire sum
);
    assign sum = a ^ b ^ c_in;
    assign c_out = ((a ^ b) & c_in) | (a & b);
endmodule