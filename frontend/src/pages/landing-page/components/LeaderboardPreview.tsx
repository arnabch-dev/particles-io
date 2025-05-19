
import { LeaderboardCard } from '../../../components/LeaderboardCard';

// Mock leaderboard data
const leaderboardData = [
  { rank: 1, name: "Nebula_X", score: 12843, highlight: true },
  { rank: 2, name: "QuantumPlayer", score: 10567, highlight: false },
  { rank: 3, name: "CosmicGamer", score: 9834, highlight: false },
  { rank: 4, name: "StarDust404", score: 8721, highlight: false },
  { rank: 5, name: "NeonHunter", score: 7654, highlight: false },
];

const LeaderboardPreview = () => {
  return (
    <LeaderboardCard leaderboardData={leaderboardData}/>
  );
};

export default LeaderboardPreview;
