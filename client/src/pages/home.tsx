import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine } from "react-icons/ri";
import { Outlet } from "react-router-dom";

const Home = () => {
  return (
    <div className="Home_Container">
      <div className='Header_Container'>
        <span><PiDiamondsFourFill /> EchoCart</span>
        <section className="Search_Container">
          <p><IoSearch /></p>
          <input type="text" placeholder="Search anything..." />
          <p><RiSpeakLine /></p>
        </section>
        <section className="RightHand_Container">
          <p className="Exclusive_Store">Exclusive Store</p>
          <p><IoIosNotificationsOutline /></p>
          <div className="Image_Container">

          </div>
        </section>

      </div>
      <section className="Home_Sidebar"></section>
      <Outlet />



    </div>
  )
}

export default Home;