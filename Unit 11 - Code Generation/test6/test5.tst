load,
output-file test6.out,
output-list RAM[5000]%D1.6.1 RAM[5001]%D1.6.1 RAM[5002]%D1.6.1 RAM[5003]%D1.6.1;

repeat 1000000 {
  vmstep;
}

output;
