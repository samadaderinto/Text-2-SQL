import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useNavigate } from 'react-router-dom';
import ProfileImg from "../assets/profileimg.jfif";
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';

export const Header = () => {
  const [menu, setMenu] = useState(false);
  const [listen, setListen] = useState(false);
  const [voice, setVoice] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const nav = useNavigate();
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [store, setStore] = useState<{ name: string, email: string }>({ name: "", email: "" });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]); // To hold chunks of audio data

  useEffect(() => {
    const fetchStoreName = async () => {
      try {
        const response = await api.get(`/settings/store/get/`);
        setStore(response.data);
      } catch (error) {
        console.error('Error fetching store name:', error);
      }
    };

    fetchStoreName();
  }, []);

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop()); // Stop previous tracks if any
        }
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;

        audioChunksRef.current = []; // Reset the chunks array

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data); // Store chunks of audio data
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setAudioBlob(audioBlob); // Set the final audio blob
          console.log("Recording complete and data available");
        };

        mediaRecorder.start();
        setIsRecording(true);
        console.log("Recording started");
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    } else {
      console.error('getUserMedia not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop()); // Stop the tracks
      setIsRecording(false);
      console.log("Recording stopped");
    }
  };

  useEffect(() => {
    if (listen) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [listen]);

  const handleUpload = async () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append('file', new File([audioBlob], 'audio.webm', { type: 'audio/webm' }));

      try {
        const response = await api.post(`/query/upload/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log(response.data);
      } catch (error) {
        console.error('Error uploading audio:', error);
      }
    } else {
      console.error('No audio data available for upload.');
    }
  };

  return (
    <div className='Header_Container'>
      <span><PiDiamondsFourFill /> EchoCart</span>
      <section className="Search_Container">
        {listen ? (
          <>
            <span>Listening...</span>
            <p><FaEarListen /></p>
          </>
        ) : (
          <>
            <p className="Header_Search_Icon"><IoSearch /></p>
            <input type="text" placeholder="Search anything..." />
            <p onClick={() => setVoice(!voice)}><RiSpeakLine /></p>
          </>
        )}
      </section>
      <section className="RightHand_Container">
        <p className="Exclusive_Store">{store.name ? store.name : "Store Name"}</p>
        <p><IoIosNotificationsOutline /></p>
        <div className="Image_Container">
          <img src={ProfileImg} alt="profile" />
        </div>
      </section>
      <p onClick={() => setMenu(!menu)} className="Mobile_Menu"><RxDropdownMenu /></p>
      {menu && (
        <article className="Mobile_Menu_Nav">
          {sideBarArrayList.map((obj, index) => (
            <span
              key={index}
              onClick={() => {
                setActiveIndex(index);
                setMenu(false);
                nav(`/${obj.itemName}`);
              }}
              className={activeIndex === index ? 'Active_List' : ''}
            >
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
            </span>
          ))}
        </article>
      )}
      {voice && (
        <span
          onClick={() => {
            setVoice(false);
            setListen(true);
          }}
          className="Search_By_Voice"
        >
          Search By Voice
        </span>
      )}
      {listen && (
        <span
          onClick={() => {
            setListen(false);
            handleUpload();
          }}
          className="Search_By_Voice Stop_Voice"
        >
          Stop recording
        </span>
      )}
    </div>
  );
};
