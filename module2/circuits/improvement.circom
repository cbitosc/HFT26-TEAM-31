pragma circom 2.1.0;

include "circomlib/circuits/comparators.circom";

template Improvement() {
    signal input s1; // private: score_v1
    signal input s2; // private: score_v2
    signal input log_hash_v1; // public: binds to v1 trace hash
    signal input log_hash_v2; // public: binds to v2 trace hash
    signal output diff;
    signal output valid;

    diff <== s2 - s1;

    // Enforce diff > 0 using comparator: s2 > s1
    component gt = GreaterThan(32);
    gt.in[0] <== s2;
    gt.in[1] <== s1;
    gt.out === 1;

    valid <== gt.out;
}

component main {public [log_hash_v1, log_hash_v2]} = Improvement();

