module full_adder_using_decoder  (
    a,b,cin,sum,carry
);


input a,b,cin;
output sum,carry;

wire [7:0]m;

decoder m1 (.in({a,b,cin}), .out(m));

assign sum = m[1] | m[2] | m[4] | m[7] ;
assign carry = m[3] | m[5] | m[6] | m[7];

    
endmodule