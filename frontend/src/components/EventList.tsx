import React from 'react';
import { GitHubEvent } from '../types';
import { formatEventMessage } from '../utils/formatters';

interface EventListProps {
    events: GitHubEvent[];
    isLoading: boolean;
    error: string | null;
}

const EventList: React.FC<EventListProps> = ({ events, isLoading, error }) => {
    if (isLoading) {
        return <div className="text-center p-4">Loading events...</div>;
    }

    if (error) {
        return <div className="text-center p-4 text-red-600">Error: {error}</div>;
    }

    if (!events.length) {
        return <div className="text-center p-4">No events found</div>;
    }

    const getActionColor = (action: string) => {
        switch (action) {
            case 'PUSH':
                return 'bg-green-100 text-green-800';
            case 'PULL_REQUEST':
                return 'bg-blue-100 text-blue-800';
            case 'MERGE':
                return 'bg-purple-100 text-purple-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="space-y-4">
            {events.map((event) => (
                <div
                    key={event.request_id}
                    className="border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className={`px-2 py-1 rounded-full text-sm font-medium ${getActionColor(event.action)}`}>
                            {event.action}
                        </span>
                        <span className="text-sm text-gray-500">
                            {event.timestamp}
                        </span>
                    </div>
                    <p className="text-gray-700">
                        {formatEventMessage(event)}
                    </p>
                    <div className="mt-2 text-sm">
                        {event.action !== 'PUSH' && (
                            <div className="flex items-center gap-2 text-gray-600">
                                <code className="bg-gray-100 px-1 rounded">{event.from_branch}</code>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                                <code className="bg-gray-100 px-1 rounded">{event.to_branch}</code>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default EventList; 