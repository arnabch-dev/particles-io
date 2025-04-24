import { useParams } from "react-router"
export default function index() {
    const params = useParams()
  const room = params?.room
  return (
    <div className="text-black">index:{room}</div>
  )
}
