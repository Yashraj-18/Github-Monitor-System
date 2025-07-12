export type GitHubEvent = {
    request_id: string;
    author: string;
    action: 'PUSH' | 'PULL_REQUEST' | 'MERGE';
    from_branch: string | null;
    to_branch: string;
    timestamp: string;
}

export type EventsResponse = {
    status: 'success' | 'error';
    count: number;
    events: GitHubEvent[];
    message?: string;
} 