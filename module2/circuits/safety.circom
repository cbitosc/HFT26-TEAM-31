pragma circom 2.1.0;

template Safety() {
    signal input bannedCount;
    signal output valid;

    bannedCount === 0;
    valid <== 1;
}

component main = Safety();

