require_relative '../main'


describe Main do
  let(:udp_client) { double 'udp_client' }
  let(:joy_stick) { double 'joy_stick' }

  before :each do
    allow(UDPClient).to receive(:new).and_return udp_client
    allow(JoyStick).to receive(:new).and_return joy_stick
  end

  it 'should connect to the robot via UDP' do
    expect(UDPClient).to receive :new
    Main.new
  end

  it 'should initialize the joystick' do
    expect(JoyStick).to receive :new
    Main.new
  end
end
