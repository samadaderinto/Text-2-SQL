import { useNavigate } from "react-router-dom";


export const PageNotFound = () => {
  const nav = useNavigate()
  return (
    <div className="Not_Found_Container">
      <div className="Content_container">
        <span className="Not_Found_Brand">ECHOCART</span>
        <div className="Not_Found_Code" aria-hidden="true">404</div>
        <h1>This page took a wrong turn.</h1>
        <p>The page you’re looking for doesn’t exist or may have moved.</p>
        <div className="Not_Found_Actions">
          <button type="button" className="Not_Found_Primary" onClick={() => nav('/dashboard')}>
            Go to dashboard
          </button>
          <button type="button" className="Not_Found_Secondary" onClick={() => nav(-1)}>
            Go back
          </button>
        </div>
      </div>
    </div>
  )
}