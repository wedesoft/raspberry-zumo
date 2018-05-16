require_relative '../main'


describe Main do
  let(:udp_client) { double 'udp_client' }
  let(:joystick) { double 'joystick' }

  before :each do
    allow(UDPClient).to receive(:new).and_return udp_client
    allow(Joystick).to receive(:new).and_return joystick
    allow(joystick).to receive :update
    allow(udp_client).to receive :write
  end

  describe :initialize do
    it 'should connect to the robot via UDP' do
      expect(UDPClient).to receive :new
      Main.new
    end

    it 'should initialize the joystick' do
      expect(Joystick).to receive :new
      Main.new
    end
  end

  describe :update do
    it 'should update the joystick' do
      expect(joystick).to receive :update
      Main.new.update
    end

    it 'should send the axes values' do
      expect(udp_client).to receive(:write).with '0,0'
      Main.new.update
    end
  end
end
