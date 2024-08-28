import { useNavigate } from "react-router-dom";


export const PageNotFound = () => {
  const nav = useNavigate()
  return (
    <div className="Not_Found_Container">


      <div className="Content_container">
        <h1>Oops! Page Not Found</h1>
        <p>It looks like the page you are looking for doesn't exist or has moved</p>
        <p>Don't worry, you can always go back to your dashboard or try searching what you need!</p>
        <button onClick={() => nav(-1)}>
          back
        </button>
      </div>
    </div>
  )
}

  ;