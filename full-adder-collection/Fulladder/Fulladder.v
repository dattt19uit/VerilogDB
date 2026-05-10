module fulladder(X,Y,Ci,S,Co);
input X,Y,Ci;
output S,Co;
assign S=X^Y^Ci;
assign Co=(X&Y)|(Y&Ci)|(Ci&X);
endmodule