"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface UrlData {
  short_code: string;
  original_url: string;
  click_count: number;
  created_at: string;
}

export default function Home() {
  const [url, setUrl] = useState("");
  const [links, setLinks] = useState<UrlData[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchLinks = async () => {
    try {
      const res = await fetch("/api/link/all_links");
      const data = await res.json();
      if (Array.isArray(data)) {
        setLinks(data);
      }
    } catch (error) {
      console.error("Error fetching links", error);
    }
  };

  useEffect(() => {
    fetchLinks();
  }, []);

  const handleShorten = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    
    try {
      const res = await fetch("/api/link/shorten", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original_url: url })
      });
      if (res.ok) {
        setUrl("");
        fetchLinks(); // Refresh the list after successful shortening
      }
    } catch (error) {
      console.error("Error shortening URL", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8" suppressHydrationWarning>
      <div className="max-w-4xl w-full space-y-8 text-black" suppressHydrationWarning>
        
        {/* Header & Form Section */}
        <div className="bg-white p-8 rounded-xl shadow-md text-center" suppressHydrationWarning>
          <h1 className="text-4xl font-extrabold text-blue-600 mb-4">URL Kısaltıcı</h1>
          <p className="text-gray-500 mb-8">Uzun linklerinizi kolayca paylaşılabilir hale getirin.</p>
          
          <form onSubmit={handleShorten} className="flex gap-4 max-w-2xl mx-auto">
            <input
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-black"
              placeholder="https://cok-uzun-bir-link.com"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50"
            >
              {loading ? "Bekleyin..." : "Kısalt"}
            </button>
          </form>
        </div>

        {/* Links List Section */}
        <div className="bg-white p-8 rounded-xl shadow-md" suppressHydrationWarning>
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Oluşturulan Linkler</h2>
          
          <div className="overflow-x-auto" suppressHydrationWarning>
            <table className="min-w-full text-left border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-100 text-gray-600 text-sm uppercase tracking-wider">
                  <th className="py-4 px-6 font-semibold">Kısa Kod</th>
                  <th className="py-4 px-6 font-semibold">Orijinal URL</th>
                  <th className="py-4 px-6 font-semibold text-center">Tıklanma</th>
                  <th className="py-4 px-6 font-semibold text-right">İşlem</th>
                </tr>
              </thead>
              <tbody className="text-gray-700">
                {links.map((link) => (
                  <tr key={link.short_code} className="border-b border-gray-50 hover:bg-gray-50 transition">
                    <td className="py-4 px-6 font-medium text-blue-600">
                      <a href={`/api/link/${link.short_code}`} target="_blank" rel="noreferrer" className="hover:underline">
                        /{link.short_code}
                      </a>
                    </td>
                    <td className="py-4 px-6 truncate max-w-xs text-sm" title={link.original_url}>
                      {link.original_url}
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-bold">
                        {link.click_count}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <Link 
                        href={`/${link.short_code}`}
                        className="text-sm text-gray-500 hover:text-blue-600 underline font-medium"
                      >
                        Detaylar ▸
                      </Link>
                    </td>
                  </tr>
                ))}
                {links.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-gray-500">
                      Henüz hiç link oluşturulmamış.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </main>
  );
}