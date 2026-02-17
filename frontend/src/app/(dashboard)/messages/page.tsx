"use client";

import { useState } from "react";
import { Send, Search } from "lucide-react";
import { Header } from "@/components/layouts/header";
import { useAuth } from "@/lib/hooks/use-auth";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

interface Message {
  id: string;
  senderId: string;
  text: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  participantName: string;
  participantRole: string;
  lastMessage: string;
  lastMessageTime: string;
  unread: number;
  messages: Message[];
}

const MOCK_CONVERSATIONS: Conversation[] = [
  {
    id: "conv-1",
    participantName: "Maria Santos",
    participantRole: "Freelancer",
    lastMessage: "I can have the draft ready by Friday. Does that work?",
    lastMessageTime: "2026-02-16T10:30:00Z",
    unread: 2,
    messages: [
      {
        id: "m-1",
        senderId: "editor",
        text: "Hi Maria, thanks for your pitch on carbon credits. We'd love to move forward with this.",
        timestamp: "2026-02-15T09:00:00Z",
      },
      {
        id: "m-2",
        senderId: "freelancer",
        text: "That's great news! I'm excited to get started. When would you need the first draft?",
        timestamp: "2026-02-15T09:15:00Z",
      },
      {
        id: "m-3",
        senderId: "editor",
        text: "We're targeting a March publication. Could you aim for a first draft by end of next week?",
        timestamp: "2026-02-15T14:00:00Z",
      },
      {
        id: "m-4",
        senderId: "freelancer",
        text: "I can have the draft ready by Friday. Does that work?",
        timestamp: "2026-02-16T10:30:00Z",
      },
    ],
  },
  {
    id: "conv-2",
    participantName: "James Okafor",
    participantRole: "Freelancer",
    lastMessage: "I've updated the sourcing section as requested.",
    lastMessageTime: "2026-02-15T16:45:00Z",
    unread: 0,
    messages: [
      {
        id: "m-5",
        senderId: "editor",
        text: "James, could you strengthen the sourcing in your heat island piece? We need at least two more on-the-record sources.",
        timestamp: "2026-02-14T11:00:00Z",
      },
      {
        id: "m-6",
        senderId: "freelancer",
        text: "Sure thing. I have a few contacts I can reach out to. I'll update the draft.",
        timestamp: "2026-02-14T13:20:00Z",
      },
      {
        id: "m-7",
        senderId: "freelancer",
        text: "I've updated the sourcing section as requested.",
        timestamp: "2026-02-15T16:45:00Z",
      },
    ],
  },
  {
    id: "conv-3",
    participantName: "Priya Sharma",
    participantRole: "Freelancer",
    lastMessage: "Looking forward to discussing the summer feature timeline.",
    lastMessageTime: "2026-02-14T09:00:00Z",
    unread: 1,
    messages: [
      {
        id: "m-8",
        senderId: "editor",
        text: "Hi Priya, your regenerative agriculture pitch was accepted! Let's discuss timing.",
        timestamp: "2026-02-13T15:00:00Z",
      },
      {
        id: "m-9",
        senderId: "freelancer",
        text: "Looking forward to discussing the summer feature timeline.",
        timestamp: "2026-02-14T09:00:00Z",
      },
    ],
  },
  {
    id: "conv-4",
    participantName: "Dev Editor",
    participantRole: "Editor",
    lastMessage: "Let me know if you need any additional resources for the piece.",
    lastMessageTime: "2026-02-13T11:30:00Z",
    unread: 0,
    messages: [
      {
        id: "m-10",
        senderId: "editor",
        text: "Welcome to the project! Here are the guidelines for the assignment.",
        timestamp: "2026-02-12T10:00:00Z",
      },
      {
        id: "m-11",
        senderId: "freelancer",
        text: "Thanks! I've reviewed everything. I have a few questions about the scope.",
        timestamp: "2026-02-12T14:00:00Z",
      },
      {
        id: "m-12",
        senderId: "editor",
        text: "Let me know if you need any additional resources for the piece.",
        timestamp: "2026-02-13T11:30:00Z",
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatMessageTime(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  }
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) {
    return date.toLocaleDateString("en-US", { weekday: "short" });
  }
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatFullTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MessagesPage() {
  const { user } = useAuth();
  const [selectedId, setSelectedId] = useState<string>(MOCK_CONVERSATIONS[0].id);
  const [searchQuery, setSearchQuery] = useState("");
  const [newMessage, setNewMessage] = useState("");
  const [conversations, setConversations] =
    useState<Conversation[]>(MOCK_CONVERSATIONS);

  const currentUserId = user?.role === "editor" ? "editor" : "freelancer";

  const filtered = searchQuery.trim()
    ? conversations.filter((c) =>
        c.participantName.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : conversations;

  const selectedConv = conversations.find((c) => c.id === selectedId);

  function handleSend() {
    if (!newMessage.trim() || !selectedConv) return;

    const msg: Message = {
      id: `m-${Date.now()}`,
      senderId: currentUserId,
      text: newMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setConversations((prev) =>
      prev.map((c) =>
        c.id === selectedId
          ? {
              ...c,
              messages: [...c.messages, msg],
              lastMessage: msg.text,
              lastMessageTime: msg.timestamp,
            }
          : c
      )
    );
    setNewMessage("");
  }

  return (
    <>
      <Header title="Messages" />
      <div className="flex flex-1 overflow-hidden">
        {/* Conversation list */}
        <div className="flex w-[320px] shrink-0 flex-col border-r border-ink-200 bg-white">
          {/* Search */}
          <div className="border-b border-ink-200 p-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-8 w-full rounded-[3px] border border-ink-200 bg-ink-50 pl-8 pr-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
              />
            </div>
          </div>

          {/* Conversation list */}
          <div className="flex-1 overflow-y-auto">
            {filtered.map((conv) => {
              const isSelected = conv.id === selectedId;
              return (
                <button
                  key={conv.id}
                  onClick={() => setSelectedId(conv.id)}
                  className={`flex w-full items-start gap-3 border-b border-ink-100 px-4 py-3 text-left transition-colors ${
                    isSelected ? "bg-ink-50" : "hover:bg-ink-50/50"
                  }`}
                >
                  {/* Avatar */}
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink-200 text-xs font-medium text-ink-700">
                    {conv.participantName
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <p className="truncate text-sm font-medium text-ink-950">
                        {conv.participantName}
                      </p>
                      <span className="ml-2 shrink-0 text-[11px] text-ink-400">
                        {formatMessageTime(conv.lastMessageTime)}
                      </span>
                    </div>
                    <div className="mt-0.5 flex items-center justify-between">
                      <p className="truncate text-xs text-ink-500">
                        {conv.lastMessage}
                      </p>
                      {conv.unread > 0 && (
                        <span className="ml-2 flex h-4 min-w-4 shrink-0 items-center justify-center rounded-full bg-accent-600 px-1 text-[10px] font-medium text-white">
                          {conv.unread}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}

            {filtered.length === 0 && (
              <div className="p-6 text-center">
                <p className="text-sm text-ink-500">No conversations found</p>
              </div>
            )}
          </div>
        </div>

        {/* Chat area */}
        {selectedConv ? (
          <div className="flex flex-1 flex-col bg-ink-50">
            {/* Chat header */}
            <div className="flex items-center gap-3 border-b border-ink-200 bg-white px-5 py-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-200 text-xs font-medium text-ink-700">
                {selectedConv.participantName
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </div>
              <div>
                <p className="text-sm font-medium text-ink-950">
                  {selectedConv.participantName}
                </p>
                <p className="text-xs text-ink-400">
                  {selectedConv.participantRole}
                </p>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-5 py-4">
              <div className="mx-auto max-w-2xl space-y-3">
                {selectedConv.messages.map((msg) => {
                  const isMe = msg.senderId === currentUserId;
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isMe ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[75%] rounded-[5px] px-3.5 py-2 ${
                          isMe
                            ? "bg-ink-950 text-white"
                            : "border border-ink-200 bg-white text-ink-900"
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{msg.text}</p>
                        <p
                          className={`mt-1 text-right text-[10px] ${
                            isMe ? "text-ink-400" : "text-ink-400"
                          }`}
                        >
                          {formatFullTime(msg.timestamp)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Message input */}
            <div className="border-t border-ink-200 bg-white px-5 py-3">
              <div className="mx-auto flex max-w-2xl items-center gap-2">
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  className="h-9 flex-1 rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                />
                <button
                  onClick={handleSend}
                  disabled={!newMessage.trim()}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-[3px] bg-ink-950 text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-1 items-center justify-center bg-ink-50">
            <p className="text-sm text-ink-400">
              Select a conversation to start messaging
            </p>
          </div>
        )}
      </div>
    </>
  );
}
