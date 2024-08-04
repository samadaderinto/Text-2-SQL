import  { ReactElement,  useState, useRef } from "react";
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
  const [audio, setAudio] = useState<Blob | null>(null)
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        // You can handle the audioBlob or audioUrl here, e.g., upload it or save it
        setAudio(audioBlob)
        console.log(audio)
        console.log('Recording stopped. Audio URL:', audioUrl);
        audioChunksRef.current = [];
      };

      mediaRecorder.start();
      setIsRecording(true);
    } else {
      console.error('getUserMedia not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };


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

  if (listen) {
    startRecording()
  } else {
    stopRecording()
  }

  return (
    <div className="Home_Container">
      <div className='Header_Container'>
        <span><PiDiamondsFourFill /> EchoCart</span>
        <section className="Search_Container">


          {
            listen? 
            <>
            <p onClick={()=> listen? setListen(false): null}>stop</p>
            <p><FaEarListen/></p>
            </>
             : 
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