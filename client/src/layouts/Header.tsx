import { useState, ReactElement, useRef } from 'react';
import { RxDropdownMenu } from "react-icons/rx";
import { FaEarListen } from "react-icons/fa6";
import { RiSpeakLine } from "react-icons/ri";
import { PiDiamondsFourFill } from "react-icons/pi";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoPeopleOutline, IoSearch, IoSettingsOutline } from "react-icons/io5";
import { IoPeopleOutline, IoSearch, IoSettingsOutline } from "react-icons/io5";
import { RiShoppingBag3Line } from "react-icons/ri";
import { RxDashboard } from 'react-icons/rx';
import { RxDashboard } from 'react-icons/rx';
import { RiLogoutBoxLine } from "react-icons/ri";
import { MdOutlineShoppingCart } from "react-icons/md";
import { useNavigate } from 'react-router-dom';

export const Header = () => {
  const [menu, setMenu] = useState(false);
  const [listen, setListen] = useState(false);
  const [voice, setVoice] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const Nav = useNavigate();
  const [audio, setAudio] = useState<Blob | null>(null);
  const [listen, setListen] = useState(false);
  const [voice, setVoice] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const Nav = useNavigate();
  const [audio, setAudio] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  interface Item {
    icon: ReactElement;
    itemName: string;
  interface Item {
    icon: ReactElement;
    itemName: string;
  }

  const sideBarArrayList: Item[] = [
    {
      icon: <RxDashboard />,
      itemName: 'dashboard'
    },
    {
      icon: <RiShoppingBag3Line />,
      itemName: 'product'
    },
    {
      icon: <MdOutlineShoppingCart />,
      itemName: 'orders'
    },
    {
      icon: <IoPeopleOutline />,
      itemName: 'customers'
    },
    {
      icon: <IoSettingsOutline />,
      itemName: 'settings'
    },
    {
      icon: <RiLogoutBoxLine />,
      itemName: 'logout'
    }
  ];

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
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
          setAudio(audioBlob);
          console.log(audio);
          console.log('Recording stopped. Audio URL:', audioUrl);
          audioChunksRef.current = [];
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Permission denied. Please allow access to the microphone.');
      }
    } else {
      console.error('getUserMedia not supported on this browser.');
      alert('getUserMedia is not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  if (listen) {
    startRecording();
  } else {
    stopRecording();
  }

  return (
    <div className='Header_Container'>
      <span><PiDiamondsFourFill /> EchoCart</span>
      <section className="Search_Container">
        {
          listen ?
            <>
              <span>Listening...</span>
              <p><FaEarListen /></p>
            </>
            :
            <>
              <p className="Header_Search_Icon"><IoSearch /></p>
              <input type="text" placeholder="Search anything..." />
              <p onClick={() => setVoice(!voice)}><RiSpeakLine /></p>
            </>
        }
      </section>
      <section className="RightHand_Container">
        <p className="Exclusive_Store">Exclusive Store</p>
        <p><IoIosNotificationsOutline /></p>
        <div className="Image_Container"></div>
      </section>
      <p onClick={() => setMenu(!menu)} className="Mobile_Menu"><RxDropdownMenu /></p>
      {
        menu &&
        (
          <article className="Mobile_Menu_Nav">
            {
              sideBarArrayList.map((obj, index) => (
                <span
                  key={index}
                  onClick={() => {
                    setActiveIndex(index);
                    setMenu(false);
                    Nav(`/${obj.itemName}`);
                  }}
                  className={activeIndex === index ? 'Active_List' : ''}
                >
                  <p className="List_icon">{obj.icon}</p>
                  <p>{obj.itemName}</p>
                </span>
              ))
            }
          </article>
        )
      }
      {
        voice && <span onClick={() => {
          setVoice(false);
          setListen(true);
        }} className="Search_By_Voice">Search By Voice</span>
      }
      {
        listen && <span onClick={() => setListen(false)} className="Search_By_Voice Stop_Voice">Stop recording</span>
      }
    </div>
  );
};
