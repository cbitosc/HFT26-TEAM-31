// SPDX-License-Identifier: GPL-3.0
/*
    Copyright 2021 0KIMS association.

    This file is generated with [snarkJS](https://github.com/iden3/snarkjs).

    snarkJS is a free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    snarkJS is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    along with snarkJS. If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.7.0 <0.9.0;

contract Groth16Verifier {
    // Scalar field size
    uint256 constant r    = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Base field size
    uint256 constant q   = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // Verification Key data
    uint256 constant alphax  = 12431943776132722768106808313695010979484395832868525884219227421463961674798;
    uint256 constant alphay  = 19287515849954915707575025408754326203817136290794731690779323538156227062873;
    uint256 constant betax1  = 1010811899513163087724115458595224154412319772073410606873911428267594656411;
    uint256 constant betax2  = 9497851784392193591361218407065212831685623274456692724338161996749292925907;
    uint256 constant betay1  = 15536559800183397048160096454813442633369834129464826560521675469841466237010;
    uint256 constant betay2  = 5170570950214377378304492138699102418047038172975249581770113034045415518299;
    uint256 constant gammax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant gammax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant gammay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant gammay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;
    uint256 constant deltax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant deltax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant deltay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant deltay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;

    
    uint256 constant IC0x = 21821105834750512461310487614662036300308288420116225625781110409503622363452;
    uint256 constant IC0y = 20543350770426809495775573960849769682065314196318179469375834139231986123197;
    
    uint256 constant IC1x = 18540443963167857483158590149399272416607656738562114639729977666309134043915;
    uint256 constant IC1y = 15102844388263236504494852939333436309975197381936827562107445703782934015274;
    
    uint256 constant IC2x = 4452638806731940449645638828071064508067960031648788076317141839293872152974;
    uint256 constant IC2y = 3085235021412769637208007799553945786470950710749652150181253003683264485370;
    
    uint256 constant IC3x = 1748581981399460663017197789017957498820845813441609660295938035104920902143;
    uint256 constant IC3y = 21746588734678758840433710889419437922355514955550779233204826320022478113549;
    
    uint256 constant IC4x = 10183577655039207773094244385874581721806292142009568258642015048382820766360;
    uint256 constant IC4y = 20819065006498631232429490493922256450950211124436061063895096707709661694688;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[4] calldata _pubSignals) public view returns (bool) {
        assembly {
            function checkField(v) {
                if iszero(lt(v, r)) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }
            
            // G1 function to multiply a G1 value(x,y) to value in an address
            function g1_mulAccC(pR, x, y, s) {
                let success
                let mIn := mload(0x40)
                mstore(mIn, x)
                mstore(add(mIn, 32), y)
                mstore(add(mIn, 64), s)

                success := staticcall(sub(gas(), 2000), 7, mIn, 96, mIn, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }

                mstore(add(mIn, 64), mload(pR))
                mstore(add(mIn, 96), mload(add(pR, 32)))

                success := staticcall(sub(gas(), 2000), 6, mIn, 128, pR, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }

            function checkPairing(pA, pB, pC, pubSignals, pMem) -> isOk {
                let _pPairing := add(pMem, pPairing)
                let _pVk := add(pMem, pVk)

                mstore(_pVk, IC0x)
                mstore(add(_pVk, 32), IC0y)

                // Compute the linear combination vk_x
                
                g1_mulAccC(_pVk, IC1x, IC1y, calldataload(add(pubSignals, 0)))
                
                g1_mulAccC(_pVk, IC2x, IC2y, calldataload(add(pubSignals, 32)))
                
                g1_mulAccC(_pVk, IC3x, IC3y, calldataload(add(pubSignals, 64)))
                
                g1_mulAccC(_pVk, IC4x, IC4y, calldataload(add(pubSignals, 96)))
                

                // -A
                mstore(_pPairing, calldataload(pA))
                mstore(add(_pPairing, 32), mod(sub(q, calldataload(add(pA, 32))), q))

                // B
                mstore(add(_pPairing, 64), calldataload(pB))
                mstore(add(_pPairing, 96), calldataload(add(pB, 32)))
                mstore(add(_pPairing, 128), calldataload(add(pB, 64)))
                mstore(add(_pPairing, 160), calldataload(add(pB, 96)))

                // alpha1
                mstore(add(_pPairing, 192), alphax)
                mstore(add(_pPairing, 224), alphay)

                // beta2
                mstore(add(_pPairing, 256), betax1)
                mstore(add(_pPairing, 288), betax2)
                mstore(add(_pPairing, 320), betay1)
                mstore(add(_pPairing, 352), betay2)

                // vk_x
                mstore(add(_pPairing, 384), mload(add(pMem, pVk)))
                mstore(add(_pPairing, 416), mload(add(pMem, add(pVk, 32))))


                // gamma2
                mstore(add(_pPairing, 448), gammax1)
                mstore(add(_pPairing, 480), gammax2)
                mstore(add(_pPairing, 512), gammay1)
                mstore(add(_pPairing, 544), gammay2)

                // C
                mstore(add(_pPairing, 576), calldataload(pC))
                mstore(add(_pPairing, 608), calldataload(add(pC, 32)))

                // delta2
                mstore(add(_pPairing, 640), deltax1)
                mstore(add(_pPairing, 672), deltax2)
                mstore(add(_pPairing, 704), deltay1)
                mstore(add(_pPairing, 736), deltay2)


                let success := staticcall(sub(gas(), 2000), 8, _pPairing, 768, _pPairing, 0x20)

                isOk := and(success, mload(_pPairing))
            }

            let pMem := mload(0x40)
            mstore(0x40, add(pMem, pLastMem))

            // Validate that all evaluations ∈ F
            
            checkField(calldataload(add(_pubSignals, 0)))
            
            checkField(calldataload(add(_pubSignals, 32)))
            
            checkField(calldataload(add(_pubSignals, 64)))
            
            checkField(calldataload(add(_pubSignals, 96)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }

/**
 * ============================================================================
 *                    AUTOEVOLVE PROTOCOL INTEGRATION SUITE
 * ============================================================================
 * @title AutoEvolveImprovementVerifier & Escrow Protocol
 * @notice Validates zero-knowledge self-improvement proofs generated during the
 *         autonomous generate-critique-revise cycle (V1 -> V2 -> V3).
 * @dev Binds zero-knowledge arithmetic satisfaction to execution trace hashes,
 *      ensuring agents only receive micro-rewards for cryptographically proven
 *      functional and performance improvements without disclosing proprietary prompts.
 */

interface IAutoEvolveVerifier {
    struct Proof {
        uint256[2] a;
        uint256[2][2] b;
        uint256[2] c;
    }

    struct VersionProof {
        uint256[2] a;
        uint256[2][2] b;
        uint256[2] c;
        uint256[4] publicSignals; // [diff, valid, log_hash_start, log_hash_end]
    }

    event ImprovementProofVerified(
        string indexed taskId,
        uint256 scoreDiff,
        uint256 logHashStart,
        uint256 logHashEnd,
        address indexed agent
    );

    event ChainProofVerified(
        string indexed taskId,
        uint256 totalImprovement,
        uint256 initialLogHash,
        uint256 finalLogHash,
        address indexed agent
    );

    event RewardEscrowed(
        string indexed taskId,
        address indexed agent,
        uint256 amountWei
    );

    event MemoryCIDCached(
        string indexed taskId,
        string cid,
        uint256 traceHash
    );
}

/**
 * @title AutoEvolveEscrowBase
 * @notice Manages escrow deposits, reputation points, and reward distribution
 */
abstract contract AutoEvolveEscrowBase {
    address public protocolTreasury;
    uint256 public constant BASE_REWARD_WEI = 0.05 ether;
    uint256 public constant MAX_REWARD_WEI = 1.00 ether;

    mapping(address => uint256) public agentReputation;
    mapping(bytes32 => bool) public processedCommitments;
    mapping(string => string) public taskMemoryCIDs;

    event RewardDeposited(address indexed funder, uint256 amount);
    event RewardWithdrawn(address indexed recipient, uint256 amount);

    function computeTaskCommitment(
        string memory taskId,
        uint256 initialHash,
        uint256 finalHash
    ) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(taskId, initialHash, finalHash));
    }

    receive() external payable {
        emit RewardDeposited(msg.sender, msg.value);
    }
}

/**
 * @title AutoEvolveImprovementVerifier
 * @notice Comprehensive settlement layer for AutoEvolve Protocol Module 4
 */
contract AutoEvolveImprovementVerifier is IAutoEvolveVerifier, AutoEvolveEscrowBase {
    Groth16Verifier public immutable zkVerifier;
    address public protocolAdmin;

    // Mapping from task ID to verified completion status
    mapping(string => bool) public verifiedTasks;
    // Mapping from task ID to total improvement points
    mapping(string => uint256) public totalGains;
    // Mapping from task ID to committed final execution trace hash
    mapping(string => uint256) public committedTraceHashes;

    modifier onlyAdmin() {
        require(msg.sender == protocolAdmin, "AutoEvolve: caller is not admin");
        _;
    }

    constructor() {
        zkVerifier = new Groth16Verifier();
        protocolAdmin = msg.sender;
        protocolTreasury = msg.sender;
    }

    /**
     * @notice Verifies a single transition proof (e.g. V1 -> V2 or V2 -> V3)
     * @param proof The Groth16 proof parameters (a, b, c)
     * @param input Public inputs: [diff, valid, log_hash_start, log_hash_end]
     * @return isValid True if proof satisfies arithmetic constraints
     */
    function verifySingleStep(
        Proof calldata proof,
        uint256[4] calldata input
    ) public view returns (bool isValid) {
        // Enforce valid == 1 (circuit comparator check)
        require(input[1] == 1, "AutoEvolve: Circuit validity signal must be 1");
        // Enforce diff > 0 (score improvement constraint)
        require(input[0] > 0, "AutoEvolve: Score diff must be strictly positive");

        return zkVerifier.verifyProof(
            proof.a,
            proof.b,
            proof.c,
            input
        );
    }

    /**
     * @notice Verifies a continuous 2-stage improvement chain (V1 -> V2 -> V3)
     * @param taskId Unique identifier of the autonomous task (e.g. lru_cache_01)
     * @param step1 Proof and public inputs for V1 -> V2 transition
     * @param step2 Proof and public inputs for V2 -> V3 transition
     * @param agent Address of the autonomous agent submitting the proof
     * @param memoryCID IPFS content identifier containing full failure logs and revision diffs
     */
    function verifyImprovementChain(
        string calldata taskId,
        VersionProof calldata step1,
        VersionProof calldata step2,
        address agent,
        string calldata memoryCID
    ) external returns (bool) {
        require(!verifiedTasks[taskId], "AutoEvolve: Task already verified and claimed");
        require(agent != address(0), "AutoEvolve: Invalid agent address");

        // 1. Verify Step 1: V1 -> V2
        require(step1.publicSignals[1] == 1, "AutoEvolve: Step 1 validity signal failed");
        require(step1.publicSignals[0] > 0, "AutoEvolve: Step 1 must have positive improvement");
        bool ok1 = zkVerifier.verifyProof(
            step1.a,
            step1.b,
            step1.c,
            step1.publicSignals
        );
        require(ok1, "AutoEvolve: Step 1 Groth16 proof verification failed");

        // 2. Verify Step 2: V2 -> V3
        require(step2.publicSignals[1] == 1, "AutoEvolve: Step 2 validity signal failed");
        require(step2.publicSignals[0] > 0, "AutoEvolve: Step 2 must have positive improvement");
        bool ok2 = zkVerifier.verifyProof(
            step2.a,
            step2.b,
            step2.c,
            step2.publicSignals
        );
        require(ok2, "AutoEvolve: Step 2 Groth16 proof verification failed");

        // 3. Cryptographic Binding: Ensure step1.end == step2.start
        // step1.publicSignals[3] is log_hash_v2, step2.publicSignals[2] must be log_hash_v2
        require(
            step1.publicSignals[3] == step2.publicSignals[2],
            "AutoEvolve: Trace hash continuity broken between V2 end and V2 start"
        );

        uint256 totalDiff = step1.publicSignals[0] + step2.publicSignals[0];
        uint256 initialHash = step1.publicSignals[2];
        uint256 finalHash = step2.publicSignals[3];

        bytes32 commitment = computeTaskCommitment(taskId, initialHash, finalHash);
        require(!processedCommitments[commitment], "AutoEvolve: Commitment replay protection triggered");
        processedCommitments[commitment] = true;

        verifiedTasks[taskId] = true;
        totalGains[taskId] = totalDiff;
        committedTraceHashes[taskId] = finalHash;
        taskMemoryCIDs[taskId] = memoryCID;
        agentReputation[agent] += totalDiff;

        emit ImprovementProofVerified(taskId, step1.publicSignals[0], step1.publicSignals[2], step1.publicSignals[3], agent);
        emit ImprovementProofVerified(taskId, step2.publicSignals[0], step2.publicSignals[2], step2.publicSignals[3], agent);
        emit ChainProofVerified(taskId, totalDiff, initialHash, finalHash, agent);
        emit MemoryCIDCached(taskId, memoryCID, finalHash);

        // Distribute micro-reward if escrow balance allows
        uint256 rewardAmount = calculateReward(totalDiff);
        if (address(this).balance >= rewardAmount && rewardAmount > 0) {
            (bool success, ) = payable(agent).call{value: rewardAmount}("");
            if (success) {
                emit RewardEscrowed(taskId, agent, rewardAmount);
            }
        }

        return true;
    }

    /**
     * @notice Helper to inspect verified task details
     * @param taskId Unique identifier of the task
     */
    function getTaskVerificationStatus(string calldata taskId)
        external
        view
        returns (
            bool isVerified,
            uint256 totalScoreGain,
            uint256 finalCommittedHash,
            string memory memoryCID
        )
    {
        return (
            verifiedTasks[taskId],
            totalGains[taskId],
            committedTraceHashes[taskId],
            taskMemoryCIDs[taskId]
        );
    }

    /**
     * @notice Helper to retrieve calculated reward tier based on verified gains
     * @param totalGain The sum of score improvements achieved
     */
    function calculateReward(uint256 totalGain) public pure returns (uint256) {
        if (totalGain == 0) return 0;
        uint256 reward = (totalGain * BASE_REWARD_WEI) / 10;
        if (reward > MAX_REWARD_WEI) {
            return MAX_REWARD_WEI;
        }
        return reward;
    }

    /**
     * @notice Allows protocol admin to update treasury recipient address
     * @param newTreasury New address for treasury distributions
     */
    function setTreasury(address newTreasury) external onlyAdmin {
        require(newTreasury != address(0), "AutoEvolve: Invalid treasury address");
        protocolTreasury = newTreasury;
    }

    /**
     * @notice Allows admin to deposit funds into reward escrow pool
     */
    function depositEscrowRewards() external payable {
        require(msg.value > 0, "AutoEvolve: Deposit must be positive");
        emit RewardDeposited(msg.sender, msg.value);
    }

    /**
     * @notice Emergency withdrawal of excess funds by protocol administrator
     * @param recipient Target address for funds
     * @param amount Amount in wei to withdraw
     */
    function emergencyWithdraw(address payable recipient, uint256 amount) external onlyAdmin {
        require(recipient != address(0), "AutoEvolve: Invalid recipient");
        require(amount <= address(this).balance, "AutoEvolve: Insufficient balance");
        recipient.transfer(amount);
        emit RewardWithdrawn(recipient, amount);
    }

    /**
     * @dev Comprehensive query method for auditing verifiable improvement histories
     * @param taskId Task identifier to audit
     * @return isVerified Whether task verification has succeeded
     * @return scoreDelta Aggregate points improved
     * @return initialTraceHash Root execution trace hash
     * @return finalTraceHash Hardened final execution trace hash
     * @return ipfsCID Associated decentralized DataDAO memory CID
     */
    function auditTaskHistory(string calldata taskId)
        external
        view
        returns (
            bool isVerified,
            uint256 scoreDelta,
            uint256 initialTraceHash,
            uint256 finalTraceHash,
            string memory ipfsCID
        )
    {
        require(verifiedTasks[taskId], "AutoEvolve: Task has not been verified");
        return (
            true,
            totalGains[taskId],
            committedTraceHashes[taskId],
            committedTraceHashes[taskId],
            taskMemoryCIDs[taskId]
        );
    }

    /**
     * @dev Batch verification query for multi-agent collective memory synchronization
     * @param taskIds Array of task identifiers to inspect
     * @return verifiedStatus Array of booleans corresponding to each task ID
     */
    function batchCheckVerification(string[] calldata taskIds)
        external
        view
        returns (bool[] memory verifiedStatus)
    {
        verifiedStatus = new bool[](taskIds.length);
        for (uint256 i = 0; i < taskIds.length; i++) {
            verifiedStatus[i] = verifiedTasks[taskIds[i]];
        }
        return verifiedStatus;
    }
}
