import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useNavigate } from 'react-router-dom';
import ProfileImg from "../assets/profileimg.jfif";
import ClipLoader from 'react-spinners/ClipLoader';
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';

export const Header = () => {
  const [menu, setMenu] = useState(false);
  const [listen, setListen] = useState(false);
  const [voice, setVoice] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [store, setStore] = useState<{ name: string, email: string }>({ name: "", email: "" });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const nav = useNavigate();

  // Fetch store name and details, no pagination or filtering
  useEffect(() => {
    const fetchStoreName = async () => {
      try {
        const response = await api.get(`/settings/store/get/`);
        setStore(response.data); // Simple fetch with no pagination/filtering
      } catch (error) {
        console.error('Error fetching store name:', error);
      }
    };

    fetchStoreName();
  }, []);

  // Function to start audio recording
  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;

        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          if (audioChunksRef.current.length > 0) {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            setAudioBlob(audioBlob);
            console.log("Recording complete and audio blob created.");
          } else {
            console.error("No audio chunks available.");
          }
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

  // Function to stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      console.log("Recording stopped");
    }
  };

  // Handle recording start/stop based on listen state
  useEffect(() => {
    if (listen) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [listen]);

  // Upload audio when recording finishes
  useEffect(() => {
    if (audioBlob) {
      handleUpload();
    }
  }, [audioBlob]);

  // Upload the audio file to the server
  const handleUpload = async () => {
    if (audioBlob) {
        const formData = new FormData();
        formData.append('file', new File([audioBlob], 'audio.webm', { type: 'audio/webm' }));

        setLoading(true);
        try {
            const response = await api.post(`/query/upload/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                nav('/query', { state: { data: response.data, header: 'Query Results' } });
            }
        } catch (error: any) {
            if (error.response && error.response.status === 500) {
                setErrorMessage('Unable to process your audio request. Please try again.');
            } else {
                setErrorMessage('Unable to find what you\'re looking for. Please try again.');
            }
            console.error('Error uploading audio:', error);
        } finally {
            setLoading(false);
        }
    } else {
        setErrorMessage('No audio data available for upload.');
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
          }}
          className="Search_By_Voice Stop_Voice">
          Stop recording
        </span>
      )}

      {loading && (
        <div className="loading-spinner">
          <ClipLoader color={"#123abc"} loading={loading} size={50} />
        </div>
      )}

      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
};
