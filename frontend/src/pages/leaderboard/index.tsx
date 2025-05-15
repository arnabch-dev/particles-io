import { useEffect, useState } from "react";
import { MessageCircle, Zap } from "lucide-react";
import NeonButton from "../landing-page/components/NeonButton";
import SectionTitle from "../landing-page/components/SectionTitle";
import { LeaderboardCard } from "../../components/LeaderboardCard";
import { LeaderboardCardProps } from "../../components/LeaderboardCard";
import { useParams } from "react-router";

export default function Leaderboard() {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardCardProps['leaderboardData']>([]);
  const params = useParams()
  const room = params?.room

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const url = import.meta.env.VITE_BACKEND_URL!
        const res = await fetch(`${url}/lobby/leaderboard/${room}`); // 👈 replace with your actual API endpoint
        const data = await res.json();

        const sortedData = Object.entries(data)
          .sort((a, b) => b[1] - a[1])
          .map(([name, score], index) => ({
            rank: index + 1,
            name,
            score,
            highlight: false, // you can add your logic here for highlighting
          }));
          // @ts-ignore
        setLeaderboardData(sortedData);
      } catch (error) {
        console.error("Failed to fetch leaderboard:", error);
      }
    };

    fetchLeaderboard();
  }, []);

  return (
    <section id="community" className="py-20 relative bg-black min-h-screen">
      <div className="container mx-auto px-4">
        <SectionTitle
          title="Join Our Community"
          subtitle="Connect with players and stay updated"
          color="purple"
        />

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="flex flex-col justify-center">
            <h3 className="text-2xl font-bold mb-4 text-neon-purple">
              Be Part of the Swarm
            </h3>
            <p className="text-gray-300 mb-6">
              Join our thriving community of players. Share strategies, find
              teammates, and participate in exclusive events and tournaments.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <NeonButton color="purple" className="flex-1">
                <MessageCircle className="mr-2 h-5 w-5" />
                Join Discord
              </NeonButton>
              <NeonButton color="blue" className="flex-1">
                <Zap className="mr-2 h-5 w-5" />
                Follow Updates
              </NeonButton>
            </div>
          </div>
          
          <LeaderboardCard leaderboardData={leaderboardData} bottomText={`${room} Leaderboard`}/>
        </div>
      </div>
    </section>
  );
}
