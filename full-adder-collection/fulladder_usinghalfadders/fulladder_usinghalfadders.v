module fulladder_usinghalfadders(input a, b, c, output sum, carry);
  wire w1, w2, w3;

  // Instantiate two half adders
  half_adder A1 (.a(a), .b(b), .sum(w1), .carry(w2));
  half_adder A2 (.a(w1), .b(c), .sum(sum), .carry(w3));

  // OR gate for carry out
  or O1(carry, w3, w2);
endmodule