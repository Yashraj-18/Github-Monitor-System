import React, { useEffect, useState } from 'react';
import EventList from './components/EventList';
import { EventsResponse, GitHubEvent } from './types';

function App() {
  const [events, setEvents] = useState<GitHubEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('');

  const fetchEvents = React.useCallback(async () => {
    try {
      const url = new URL('http://localhost:5000/events');
      if (filter) {
        url.searchParams.append('action', filter);
      }

      const response = await fetch(url.toString());
      const data: EventsResponse = await response.json();

      if (data.status === 'success') {
        setEvents(data.events);
        setError(null);
      } else {
        setError(data.message || 'Failed to fetch events');
      }
    } catch (err) {
      setError('Failed to fetch events');
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    // Initial fetch
    fetchEvents();

    // Set up polling every 15 seconds
    const interval = setInterval(fetchEvents, 15000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, [fetchEvents]); // Now fetchEvents is properly memoized

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          GitHub Events Monitor
        </h1>

        {/* Filter controls */}
        <div className="mb-6">
          <select
            className="w-full p-2 border rounded-lg"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">All Events</option>
            <option value="PUSH">Push Events</option>
            <option value="PULL_REQUEST">Pull Requests</option>
            <option value="MERGE">Merges</option>
          </select>
        </div>

        {/* Events list */}
        <EventList
          events={events}
          isLoading={isLoading}
          error={error}
        />

        {/* Auto-refresh indicator */}
        <div className="mt-4 text-center text-sm text-gray-500">
          Auto-refreshing every 15 seconds
        </div>
      </div>
    </div>
  );
}

export default App;
