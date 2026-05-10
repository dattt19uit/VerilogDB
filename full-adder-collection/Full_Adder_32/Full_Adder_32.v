module Full_Adder_32(
    input wire [31:0] a,
    input wire [31:0] b,
    input wire c_in,
    output wire c_out,
    output wire [31:0] sum
    );
    
    wire [30:0] c_inside;
    wire [31:0] in_b;
    
    assign in_b = b ^ {32{c_in}};
    
    Full_Adder_1 Adder[31:0](.a(a[31:0]), .b(in_b[31:0]), .c_in({c_inside[30:0], c_in}), .c_out({c_out, c_inside[30:0]}), .sum(sum[31:0]));
    
endmodule