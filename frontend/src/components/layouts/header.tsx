"use client";

import { useState, useRef, useEffect } from "react";
import { Bell, Search, X } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

const MOCK_NOTIFICATIONS = [
  { id: "n1", text: "Maria Santos submitted a draft for \"Carbon Credits Investigation\"", time: "10 min ago", read: false },
  { id: "n2", text: "New pitch received from James Okafor: \"Urban Heat Islands\"", time: "1 hour ago", read: false },
  { id: "n3", text: "Payment of $1,200 released to Amara Osei", time: "3 hours ago", read: true },
  { id: "n4", text: "Priya Sharma accepted the assignment for \"Regenerative Agriculture\"", time: "Yesterday", read: true },
  { id: "n5", text: "Deadline reminder: \"Climate Policy\" draft due in 2 days", time: "Yesterday", read: true },
];

const SEARCH_SUGGESTIONS = [
  { label: "Maria Santos", type: "Freelancer" },
  { label: "Carbon Credits Investigation", type: "Pitch" },
  { label: "Climate Policy Shifts in Southeast Asia", type: "Assignment" },
  { label: "City Hall Bureau", type: "Squad" },
  { label: "Urban Heat Islands", type: "Pitch" },
];

function NotificationDropdown({ onClose }: { onClose: () => void }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [onClose]);

  return (
    <div ref={ref} className="absolute right-0 top-full z-50 mt-1 w-80 rounded-[5px] border border-ink-200 bg-white shadow-lg">
      <div className="flex items-center justify-between border-b border-ink-100 px-4 py-2.5">
        <h3 className="text-sm font-semibold text-ink-950">Notifications</h3>
        <button onClick={onClose} className="text-ink-400 hover:text-ink-600">
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="max-h-80 overflow-y-auto">
        {MOCK_NOTIFICATIONS.map((n) => (
          <div
            key={n.id}
            className={`border-b border-ink-50 px-4 py-3 transition-colors hover:bg-ink-50 ${!n.read ? "bg-accent-50/40" : ""}`}
          >
            <div className="flex items-start gap-2">
              {!n.read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-accent-600" />}
              <div className={!n.read ? "" : "pl-4"}>
                <p className="text-sm text-ink-700 leading-snug">{n.text}</p>
                <p className="mt-1 text-[11px] text-ink-400">{n.time}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="border-t border-ink-100 px-4 py-2">
        <button className="text-xs font-medium text-accent-600 hover:text-accent-700">
          Mark all as read
        </button>
      </div>
    </div>
  );
}

function SearchDialog({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const filtered = query.trim()
    ? SEARCH_SUGGESTIONS.filter(
        (s) =>
          s.label.toLowerCase().includes(query.toLowerCase()) ||
          s.type.toLowerCase().includes(query.toLowerCase())
      )
    : SEARCH_SUGGESTIONS;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/20" onClick={onClose} />
      <div className="fixed left-1/2 top-[15%] z-50 w-full max-w-lg -translate-x-1/2 rounded-[5px] border border-ink-200 bg-white shadow-xl">
        <div className="flex items-center gap-3 border-b border-ink-100 px-4 py-3">
          <Search className="h-4 w-4 text-ink-400" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search freelancers, pitches, assignments..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 text-sm text-ink-900 placeholder:text-ink-400 outline-none"
          />
          <kbd className="hidden sm:inline-flex h-5 items-center rounded border border-ink-200 bg-ink-50 px-1.5 text-[10px] text-ink-400">
            ESC
          </kbd>
        </div>
        <div className="max-h-72 overflow-y-auto py-1">
          {filtered.length > 0 ? (
            filtered.map((item) => (
              <button
                key={item.label}
                onClick={onClose}
                className="flex w-full items-center justify-between px-4 py-2 text-left transition-colors hover:bg-ink-50"
              >
                <span className="text-sm text-ink-900">{item.label}</span>
                <span className="text-[11px] text-ink-400">{item.type}</span>
              </button>
            ))
          ) : (
            <div className="px-4 py-6 text-center">
              <p className="text-sm text-ink-400">No results found</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export function Header({ title, subtitle, actions }: HeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSearch, setShowSearch] = useState(false);

  return (
    <>
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-ink-200 bg-white px-8">
        <div>
          <h1 className="text-[22px] font-semibold text-ink-950 leading-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-0.5 text-sm text-ink-500">{subtitle}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {actions}
          <button
            onClick={() => setShowSearch(true)}
            className="flex h-9 w-9 items-center justify-center rounded-[3px] text-ink-500 transition-colors hover:bg-ink-100 hover:text-ink-700"
          >
            <Search className="h-4 w-4" />
          </button>
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative flex h-9 w-9 items-center justify-center rounded-[3px] text-ink-500 transition-colors hover:bg-ink-100 hover:text-ink-700"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-accent-600" />
            </button>
            {showNotifications && (
              <NotificationDropdown onClose={() => setShowNotifications(false)} />
            )}
          </div>
        </div>
      </header>
      {showSearch && <SearchDialog onClose={() => setShowSearch(false)} />}
    </>
  );
}
