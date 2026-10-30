import { NextRequest, NextResponse } from "next/server";

export interface TaskDto {
  task_id: string;
  name: string;
  description: string;
  programming_language: string;
  class_or_function_name: string;
  functional_requirements: string[];
  input_output_spec: Record<string, any>;
  constraints: string[];
  expected_behavior: string;
}

const PREDEFINED_BENCHMARKS: TaskDto[] = [
  {
    task_id: "lru_cache_01",
    name: "Least Recently Used (LRU) Cache",
    description:
      "Design and implement a high-performance Least Recently Used (LRU) Cache data structure supporting get and put in O(1) average time complexity, deterministic eviction, and defensive handling of non-hashable inputs.",
    programming_language: "python",
    class_or_function_name: "LRUCache",
    functional_requirements: [
      "get(key) returns cached value or -1 if missing.",
      "put(key, value) updates value if key exists, or inserts new key.",
      "When capacity is exceeded, evicts the least recently used item.",
      "Capacity <= 0: put is a no-op, get always returns -1.",
      "Unhashable keys safely ignored or rejected without unhandled TypeError crashes.",
      "Strict O(1) amortized throughput under high concurrency.",
    ],
    input_output_spec: {
      init: { capacity: "int" },
      get: { params: ["key: Any"], returns: "int" },
      put: { params: ["key: Any", "value: int"], returns: "None" },
    },
    constraints: [
      "Time complexity: O(1) for both get and put operations.",
      "Space complexity: O(capacity).",
      "Must not crash on invalid/unhashable types.",
    ],
    expected_behavior: "Cache evicts oldest accessed keys while maintaining O(1) lookup.",
  },
  {
    task_id: "rate_limiter_02",
    name: "API Rate Limiter (Rolling 60s Window)",
    description:
      "Implement a production-grade API Rate Limiter allowing a maximum of 5 requests per user within a rolling 60-second window. The limiter must eliminate boundary-burst vulnerabilities, maintain independent user quotas, and sanitize inputs defensively.",
    programming_language: "python",
    class_or_function_name: "RateLimiter",
    functional_requirements: [
      "allow_request(user_id, timestamp) returns True if quota is available, else False.",
      "Enforce a rolling sliding window of 60 seconds (not a fixed reset window).",
      "get_remaining_tokens(user_id, timestamp) returns integer count of available slots.",
      "Timestamps older than (timestamp - window_seconds) must be automatically pruned.",
      "Handle non-positive max_requests (reject all) and invalid user_id/timestamp gracefully.",
      "Sub-millisecond amortized latency under high traffic.",
    ],
    input_output_spec: {
      init: { max_requests: "int = 5", window_seconds: "float = 60.0" },
      allow_request: { params: ["user_id: str", "timestamp: Optional[float]"], returns: "bool" },
      get_remaining_tokens: { params: ["user_id: str", "timestamp: Optional[float]"], returns: "int" },
    },
    constraints: [
      "Strict rolling window algorithm (sliding log or sliding window counter).",
      "O(1) or O(log N) amortized query time per user.",
      "Independent state per user.",
    ],
    expected_behavior: "Strictly bounds burst requests across arbitrary 60-second intervals.",
  },
];

let customTasks: TaskDto[] = [];

export async function GET() {
  return NextResponse.json({
    benchmarks: PREDEFINED_BENCHMARKS,
    custom_tasks: customTasks,
    all_tasks: [...PREDEFINED_BENCHMARKS, ...customTasks],
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    if (!body.name || !body.description || !body.class_or_function_name) {
      return NextResponse.json(
        { error: "Missing required fields: name, description, class_or_function_name" },
        { status: 400 }
      );
    }

    const newTask: TaskDto = {
      task_id: body.task_id || `custom_${Date.now()}`,
      name: body.name,
      description: body.description,
      programming_language: body.programming_language || "python",
      class_or_function_name: body.class_or_function_name,
      functional_requirements: body.functional_requirements || [],
      input_output_spec: body.input_output_spec || {},
      constraints: body.constraints || [],
      expected_behavior: body.expected_behavior || "",
    };

    customTasks.push(newTask);
    return NextResponse.json({ success: true, task: newTask });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

