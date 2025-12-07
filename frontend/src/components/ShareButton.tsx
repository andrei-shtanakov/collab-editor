/**
 * Share button and link display
 */

import { useState, useCallback } from 'react';
import { Share2, Copy, Check, Link } from 'lucide-react';

interface ShareButtonProps {
  sessionId: string | null;
  onCreateSession?: () => Promise<void>;
  isCreating?: boolean;
}

export function ShareButton({
  sessionId,
  onCreateSession,
  isCreating = false,
}: ShareButtonProps) {
  const [copied, setCopied] = useState(false);

  const shareUrl = sessionId
    ? `${window.location.origin}/?session=${sessionId}`
    : null;

  const handleCopy = useCallback(async () => {
    if (!shareUrl) return;

    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [shareUrl]);

  // No session yet - show create button
  if (!sessionId) {
    return (
      <button
        onClick={onCreateSession}
        disabled={isCreating}
        className="flex items-center gap-2 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 
                   text-white rounded text-sm font-medium transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isCreating ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Creating...
          </>
        ) : (
          <>
            <Share2 className="w-4 h-4" />
            Create & Share
          </>
        )}
      </button>
    );
  }

  // Session exists - show share link
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 rounded text-sm">
        <Link className="w-4 h-4 text-gray-400" />
        <span className="text-gray-300 max-w-[200px] truncate font-mono">
          {sessionId}
        </span>
      </div>
      
      <button
        onClick={handleCopy}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 
                   text-white rounded text-sm transition-colors"
        title="Copy link"
      >
        {copied ? (
          <>
            <Check className="w-4 h-4 text-green-400" />
            <span className="text-green-400">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-4 h-4" />
            <span>Copy Link</span>
          </>
        )}
      </button>
    </div>
  );
}
