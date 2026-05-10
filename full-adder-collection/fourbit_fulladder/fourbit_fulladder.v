module fourbit_fulladder(
                         input [3:0] a_in,
                         input [3:0] b_in,
                         input [3:0] c_in,
                         output  [3:0] s_out,
                         output  [3:0] c_out

    );
  fulladder_dataflow fa1( 
                       .a_in(a_in[0]),
                       .b_in(b_in[0]),
                       .c_in(c_in[0]),
                       .s_out(s_out[0]),
                       .c_out(c_out[0])

    );  
    fulladder_dataflow fa2( 
                       .a_in(a_in[1]),
                       .b_in(b_in[1]),
                       .c_in(c_in[1]),
                       .s_out(s_out[1]),
                       .c_out(c_out[1])

    );  
     fulladder_dataflow fa3( 
                       .a_in(a_in[2]),
                       .b_in(b_in[2]),
                       .c_in(c_in[2]),
                       .s_out(s_out[2]),
                       .c_out(c_out[2])

    );  
     fulladder_dataflow fa4( 
                       .a_in(a_in[3]),
                       .b_in(b_in[3]),
                       .c_in(c_in[3]),
                       .s_out(s_out[3]),
                       .c_out(c_out[3])

    );    
endmodule