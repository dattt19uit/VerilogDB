module partial_full_adder(pi,si,gi,ai,bi,ci);
output pi;
output si;
output gi;
input ai;
input bi;
input ci;

wire pi2;
xor (pi,ai,bi);
xor (pi2,ai,bi);
xor (si,pi2,ci);
and (gi,ai,bi);
endmodule