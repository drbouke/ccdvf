// Acme support assistant: the ticket reply with the TypeScript SDK.
import Anthropic from "@anthropic-ai/sdk";
import { readFileSync } from "node:fs";

const policy = readFileSync("../data/refund_policy.md", "utf8");
const lines = readFileSync("../data/tickets.jsonl", "utf8").split("\n");
const ticket = JSON.parse(lines[1]); // T-1002, the same ticket

const client = new Anthropic(); // reads ANTHROPIC_API_KEY
const response = await client.messages.create({
  model: "claude-haiku-5-5",
  max_tokens: 1000, // room for thinking plus an 80-word reply
  system: "You are an Acme support agent. Reply to the customer in at " +
    "most 80 words. Apply this policy:\n" + policy,
  messages: [{ role: "user", content: ticket.text }],
});

for (const block of response.content) {
  if (block.type === "text") console.log(block.text);
}
console.log("stop_reason:", response.stop_reason);
console.log(`usage: ${response.usage.input_tokens} in, ` +
  `${response.usage.output_tokens} out`);
