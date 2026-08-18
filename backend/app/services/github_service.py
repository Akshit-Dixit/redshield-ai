import httpx
import logging
from typing import Optional

logger = logging.getLogger("redshield.github_service")

class GitHubService:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.github_token:
            self.headers["Authorization"] = f"Bearer {self.github_token}"

    async def update_commit_status(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,  # "pending", "success", "failure", "error"
        description: str,
        target_url: Optional[str] = "http://localhost:8000/docs",
        context: str = "RedShield AI Guardrail"
    ) -> bool:
        """
        Posts build status (Pending, Green Checkmark, Red Cross) to GitHub Commit API.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/statuses/{sha}"
        payload = {
            "state": state,
            "target_url": target_url,
            "description": description[:140],  # GitHub limits description to 140 chars
            "context": context
        }

        if not self.github_token:
            logger.warning(f"No GITHUB_TOKEN set. Skipping status update for {owner}/{repo}@{sha} [{state}]")
            print(f" [SIMULATED GITHUB STATUS] {owner}/{repo}@{sha} -> State: {state.upper()} | {description}")
            return True

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully posted status '{state}' to GitHub commit {sha}")
                    return True
                else:
                    logger.error(f"Failed to post status to GitHub: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                logger.error(f"Error calling GitHub Status API: {str(e)}")
                return False