module fulladder_halfadder(
    input a,b,c,
    output sum,carry
    );
    wire w1_sum1,w2_carry1,w3,w4;
    half_adder a1(a,b,w1_sum1,w2_carry1);
    half_adder a2(w1_sum1,c,sum,w3 );
    half_adder a3(w2_carry1,w3,carry,w4);
endmodule