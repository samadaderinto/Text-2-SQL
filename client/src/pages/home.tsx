import { ReactElement, useState, useRef } from "react";

import { Outlet } from "react-router-dom";
import { Dashboard } from "../Components/Dashboard";
import { Product } from "../Components/Product";
import { Orders } from "../Components/Orders";
import { Customers } from "../Components/Customers";
import { Settings } from "../Components/Settings";

import { PageNotFound } from "./PageNotFound";
import axios, {AxiosResponse } from "axios";
import { API_BASE_URL } from "../utils/api"
// import { Logout } from "../Components/Logout";

const Home = () => {

  const [activeIndex, setActiveIndex] = useState<number>(0)
  const [active, setActive] = useState('Dashboard')
  const [menu, setMenu] = useState(false);
  const [voice, setVoice] = useState(false)
  const [listen, setListen] = useState(false)
  const [audio, setAudio] = useState<Blob | null>(null)
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const Logout = async () => {


    const refreshToken = localStorage.getItem("refreshToken")

    try {

      const response: AxiosResponse = await axios.post(`${API_BASE_URL}/auth/logout/`, {
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json'
        }

      })
    console.log(response.headers)
      localStorage.removeItem('refreshToken');
      alert('logout successful')
    } catch (error) {
      alert('logout failed')
    }

  }
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
      icon: <RxDashboard />,
      itemName: 'Dashboard'
    },
    {
      icon: <RiShoppingBag3Line />,
      itemName: 'Products'
    },
    {
      icon: <MdOutlineShoppingCart />,
      itemName: 'Orders'
    },
    {
      icon: <IoPeopleOutline />,
      itemName: 'Customers'
    },
    {
      icon: <IoSettingsOutline />,
      itemName: 'Settings'
    },
    {
      icon: <RiLogoutBoxLine />,
      itemName: 'Logout'
    }
  ]

  if (listen) {
    startRecording()
  } else {
    stopRecording()
  }

  return (
    <div className="Home_Container">
      <div className="Main_Container">
        <nav className="Home_Sidebar">
          <div className="Sidebar_Container">

            {
              sideBarArrayList.map((obj, index) => (
                <span
                  key={index}
                  onClick={() => {
                    setActive(obj.itemName)
                    setActiveIndex(index)
                  }}
                  className={activeIndex === index ? 'Active_List' : ''}>
                  <p className="List_icon">{obj.icon}</p>
                  <p>{obj.itemName}</p>
                </span>
              ))


            }

          </div>
        </nav>
        <section className="Home_Content__Container">
          {
            active === 'Dashboard' ? <Dashboard /> :
              active === 'Products' ? <Product /> :
                active === 'Orders' ? <Orders /> :
                  active === 'Customers' ? <Customers /> :
                    active === 'Settings' ? <Settings /> :
                      active === 'Logout' ? <div className="Logout_Container">
                        <article>
                          <h1>Log Out?</h1>
                          <div>
                            <span onClick={Logout} className="Blue_btn">Yes</span>
                            <span onClick={() => {
                              setActiveIndex(0)
                              setActive('Dashboard')
                            }} className="White_btn">No</span>
                          </div>
                        </article>
                      </div> :
                        active === '*' ? <PageNotFound /> : null

          }
        </section>
      </div>
      <Outlet />



    </div>
  )
}

export default Home;