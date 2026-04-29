"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface StatsData {
  click_count: number;
}

export default function LinkDetail() {
  const { short_code } = useParams();
  const router = useRouter();
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`/api/link/${short_code}/stats`);
        if (!res.ok) throw new Error("Stats not found");
        
        const data = await res.json();
        setStats(data);
      } catch (error) {
        console.error("Error fetching stats", error);
      } finally {
        setLoading(false);
      }
    };
    if (short_code) fetchStats();
  }, [short_code]);

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl w-full bg-white rounded-xl shadow-md p-8 text-center">
        
        <button 
          onClick={() => router.back()}
          className="text-sm font-medium text-gray-500 hover:text-blue-600 flex items-center mb-8 transition"
        >
          ◂ Geri Dön
        </button>

        <h1 className="text-3xl font-extrabold text-gray-800 mb-2">Link Detayı</h1>
        <p className="text-gray-500 mb-10">
          Kısa kod: <span className="font-bold text-blue-600">{short_code}</span>
        </p>

        {loading ? (
          <div className="py-12 text-gray-400">Yükleniyor...</div>
        ) : stats ? (
          <div className="flex flex-col items-center">
            {/* Büyük tık sayısı */}
            <div className="h-48 w-48 rounded-full border-8 border-blue-100 flex flex-col items-center justify-center bg-blue-50 shadow-inner mb-6">
              <span className="text-6xl font-black text-blue-600">{stats.click_count}</span>
              <span className="text-sm text-blue-400 font-semibold uppercase tracking-widest mt-1">
                Tıklanma
              </span>
            </div>

            <p className="text-gray-600 max-w-sm mb-8">
              Bu link toplamda <strong>{stats.click_count}</strong> kez aktif olarak ziyaret edildi.
            </p>

            <Link 
              href={`/api/link/${short_code}`} 
              target="_blank"
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm transition"
            >
              Linki Test Et
            </Link>
          </div>
        ) : (
          <div className="py-12 text-red-500">
            Link istatistikleri bulunamadı.
          </div>
        )}
      </div>
    </main>
  );
}
