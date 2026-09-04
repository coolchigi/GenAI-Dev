// Cedar policy: allow only explicitly listed gateway tools
// ---------------------------------------------------------
// Cedar is a policy language designed for attribute-based access control (ABAC).
// This policy permits invocation of the wordCountTool and wordCountTool only.
// Any other tool call will be denied by default (Cedar is deny-by-default).
//
// Bind this policy to the mainPolicyEngine in agentcore.json (see README.md).
//
// Enforcement:
//   PASSIVE — violations are logged but the call proceeds (shadow testing)
//   ACTIVE  — violations are blocked and an error is returned to the caller
//
// Cedar policy language reference: https://www.cedarpolicy.com/

// Permit the word count tool via the gateway
permit (
  principal,
  action == AgentCore::Action::"invoke",
  resource == AgentCore::GatewayTool::"wordCountTool"
);

// Explicitly forbid calls to any other tool (belt-and-suspenders — Cedar
// is already deny-by-default, but this makes the intent explicit and
// produces a clearer violation message in the audit log).
forbid (
  principal,
  action == AgentCore::Action::"invoke",
  resource
) unless {
  resource == AgentCore::GatewayTool::"wordCountTool"
};
