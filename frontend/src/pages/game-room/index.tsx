import { useParams } from "react-router"
import Loader from "../../components/Loader"
// TODO: HTTP call to get the players in the room
export default function index() {
  const params = useParams()
  const room = params?.room
  return <Loader text={`Inside the room ${room}`}/>
}
