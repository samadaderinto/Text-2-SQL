import { Header } from "../layouts/Header";
import SideBar from "../layouts/SideBar";

export const PageNotFound = () => {
  return (
    <div className="Not_Found_Container">
      <Header/>
      <SideBar/>

      <div className="Content_container">
        <h1>Oops! Page Not Found</h1>
        <p>It looks like the page you are looking for doesn't exist or has moved</p>
        <p>Don't worry, you can always go back to your dashboard or try searching what you need!</p>
      </div>
    </div>
  )
}

;