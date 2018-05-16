require_relative '../main'


describe Main do
  let(:udp_client) { double 'udp_client' }
  let(:joystick) { double 'joystick' }

  before :each do
    allow(UDPClient).to receive(:new).and_return udp_client
    allow(Joystick).to receive(:new).and_return joystick
  end

  it 'should connect to the robot via UDP' do
    expect(UDPClient).to receive :new
    Main.new
  end

  it 'should initialize the joystick' do
    expect(Joystick).to receive :new
    Main.new
  end
end
