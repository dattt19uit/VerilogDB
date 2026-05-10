module fulladder_dataflow( 
                       input a_in,
                       input b_in,
                       input c_in,
                       output s_out,
                       output c_out

    );
assign s_out =(a_in^b_in^c_in);    
assign c_out =(a_in&b_in|b_in&c_in|a_in&c_in);    
endmodule