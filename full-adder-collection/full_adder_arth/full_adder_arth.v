module full_adder_arth (
    input a_in,
    input b_in,
    input c_in,
    output sum_out,
    output carry_out
);
 assign {carry_out, sum_out} = a_in + b_in + c_in;
 
endmodule