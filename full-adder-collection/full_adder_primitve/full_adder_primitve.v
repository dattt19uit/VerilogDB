module full_adder_primitve(
    output s_out,c_out,
    input a_in,b_in,c_in
    );
    wire s1,c1,c2;
    halfadder_primitive h1(s1,c1,a_in,b_in);
    halfadder_primitive h2(s_out,c2,s1,c_in);
    or o(c_out,c1,c2);
endmodule