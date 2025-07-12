import { GitHubEvent } from '../types';

export const formatEventMessage = (event: GitHubEvent): string => {
    switch (event.action) {
        case 'PUSH':
            return `${event.author} pushed to ${event.to_branch} on ${event.timestamp}`;
        case 'PULL_REQUEST':
            return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${event.timestamp}`;
        case 'MERGE':
            return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${event.timestamp}`;
        default:
            return `Unknown event by ${event.author} on ${event.timestamp}`;
    }
}; 