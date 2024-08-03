import React, { ReactElement,  useState, useEffect } from "react";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch, IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine,  RiShoppingBag3Line } from "react-icons/ri";
import { FaEarListen } from "react-icons/fa6";
import {  RxDashboard } from 'react-icons/rx'
import { MdOutlineShoppingCart } from "react-icons/md";
import { Outlet } from "react-router-dom";
import { Dashboard } from "../Components/Dashboard";
import { Product } from "../Components/Product";
import { Orders } from "../Components/Orders";
import { Customers } from "../Components/Customers";
import { Settings } from "../Components/Settings";

const Home = () => {

  const [activeIndex, setActiveIndex] = useState< number | null>(null)
  const [active, setActive] = useState('')
  const [voice, setVoice] = useState(false)
  const [listen, setListen] = useState(false)
  const [recording, setRecording] = useState(false)
  const [stream, setStream] = useState< MediaStream | null>(null);

  useEffect(() => {
    let timeoutId: number | null = null;

    // Cleanup function to stop the media stream
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
      }
    };
  }, [stream]);

  const startRecording = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setStream(mediaStream);
      setRecording(true);

      // Automatically stop recording after 10 seconds
      const id = setTimeout(() => {
        stopRecording();
        setRecording(false)
      }, 3000); // 10000 ms = 10 seconds

      // Use a ref to store the timeout ID
      timeoutIdRef.current = id;
    } catch (error) {
      console.error('Error accessing audio input:', error);
    }
  };

  const stopRecording = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setRecording(false);
    setListen(false)

    // Clear the timeout if it's still active
    if (timeoutIdRef.current !== null) {
      clearTimeout(timeoutIdRef.current);
    }
  };

  // Create a ref to store the timeout ID
  const timeoutIdRef = React.useRef<number | null>(null);

if (listen) {
  startRecording()
  // console.log(recording)
  // console.log(stream)
} else {
  null
}

  interface item {
    icon: ReactElement,
    itemName: string
  }

  const sideBarArrayList: item[] = [
    {
      icon: <RxDashboard/>,
      itemName: 'Dashboard'
    },
    {
      icon: <RiShoppingBag3Line/>,
      itemName: 'Products'
    },
    {
      icon: <MdOutlineShoppingCart/>,
      itemName: 'Orders'
    },
    {
      icon:<IoPeopleOutline/>,
      itemName: 'Customers'
    },
    {
      icon: <IoSettingsOutline/>,
      itemName: 'Settings'
    },
  ]

  return (
    <div className="Home_Container">
      <div className='Header_Container'>
        <span><PiDiamondsFourFill /> EchoCart</span>
        <section className="Search_Container">


          {
            listen? 
            
            <p><FaEarListen/></p> : 
            <>
            <p><IoSearch /></p>
            <input type="text" placeholder="Search anything..." />
            <p onClick={()=> {
              voice?setVoice(false): setVoice(true)}
  
            } ><RiSpeakLine /></p>
            </>
          }
        </section>
        <section className="RightHand_Container">
          <p className="Exclusive_Store">Exclusive Store</p>
          <p><IoIosNotificationsOutline /></p>
          <div className="Image_Container">

          </div>
        </section>

      </div>

      {
        voice? <span onClick={()=>{
          setVoice(false)
          setListen(true)
        }} className="Search_By_Voice">Search By Voice</span> : null
      }

     <div className="Main_Container">
     <nav className="Home_Sidebar">
        <div className="Sidebar_Container">

          {
            sideBarArrayList.map((obj, index)=> (
              <span 
              key={index}
              onClick={()=> { 
                setActive(obj.itemName)              
                setActiveIndex(index)}} 
              className={activeIndex === index? 'Active_List': ''}>
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
            </span>
            ))

            
          }

        </div>
      </nav>
      <section className="Home_Content__Container">
        {
          active === 'Dashboard'? <Dashboard/>:
          active === 'Products'? <Product/>:
          active === 'Orders'? <Orders/>:
          active === 'Customers'? <Customers/>:
          active === 'Settings'? <Settings    />: null

        }
      </section>
     </div>
      <Outlet />



    </div>
  )
}

export default Home;